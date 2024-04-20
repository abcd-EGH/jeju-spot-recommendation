import pandas as pd
from mlxtend.frequent_patterns import association_rules, apriori

class recommender:
  def __init__(self, spot, senior, rcd_data):
    self.cat_dic = {'A5_1':'자연', 'A5_2':'맛집_카페', 'A5_3': '레저관광', 'A5_4': '역사_유적지',
                    'A5_5': '테마파크', 'A5_6': '휴식_힐링', 'A5_7': '온천', 'A5_8': '쇼핑',
                    'A5_9': '문화관광', 'A5_10': '스포츠관람', 'A5_11': '지역축제', 'A5_12': '경험',
                    'A5_13': '종교', 'A5_14': '오락', 'A5_15': '도시탐방', 'A5_16': '드라마_촬영지',
                    'A5_17': '즐길거리', 'A5_18': '지인방문', 'A5_19': '출장', 'A5_20': '교육_체험',
                    'A5_21': '기타'
                   }
    self.spot = spot
    self.senior = senior
    self.rcd_data = rcd_data

  def rules_maker(self, cluster, cat_dic):
    '''
      연관성 규칙 생성
      cluster: 특정 군집에 해당하는 데이터셋
      cat_dic: 사전에 정의된 category dictionary
    '''
    cls = pd.DataFrame()
    for i,j in zip(range(1,22),cat_dic.values()):
        cls = pd.concat([cls,cluster[j]],axis=1)
    cls = cls.astype('bool')
    freq_item = apriori(cls, min_support = 0.01, use_colnames = True)
    rules = association_rules(freq_item, metric = "lift", min_threshold = 1)
    rules.sort_values('confidence', ascending = False, inplace = True)
    
    return rules

  def recommend_spot(self, category, spot):
    recommend_list = list()
    category = list(category)
    for cat_ in category:
        recommend_list.extend(list(spot[spot['CL_NM']==cat_]['TRRSRT_NM']))
    if len(recommend_list)==0:
      return # 추천해줄 카테고리가 없을 경우 '자연' 카테고리의 관광지를 추천
    else:
      return set(recommend_list)

  def rcd_demand(self, spot_set, date, rcd_data):
    if type(spot_set) == str:
      return
    spot_demand = set()
    spot_list = list(spot_set)
    for i in spot_list:
      if rcd_data.loc[rcd_data[rcd_data['TRRSRT_NM']==i].index, date].iloc[0] < 0:
        spot_demand.add(i)
    return spot_demand
    
  def answer_to_clsuter(self, answer):
    cluster_target = []

    if answer != []:
      answer_num = 3
      if len(answer) < answer_num:
        raise ValueError(f'{answer_num}개의 질문에 대한 답을 모두 입력해주세요.')
      if len(answer) > answer_num:
        raise ValueError(f'답을 {answer_num}개만 입력해주세요.')
      for num, ans in enumerate(answer):
        if type(ans) != bool:
          raise TypeError(f'{num+1}번째 답을 True 또는 False로 입력해주세요.')
          
      if (answer[0]==False) & (answer[1]==True) & (answer[2]==False):
        cluster_target.append('0_5')
      if (answer[0] == True):
        cluster_target.append('1_4')
      if (answer[0]==False) & (answer[1]==True) & (answer[2]==True):
        cluster_target.append('2_3')
      if (answer[0]==False) & (answer[1]==False):
        cluster_target.append('6_7')
      if cluster_target == []:
        cluster_target = ['0_5','1_4','2_3','6_7']
    else:
      cluster_target = ['0_5','1_4','2_3','6_7']
    return cluster_target

  def rule_to_rcd(self, rules, act_wanted, non_recmd, sub_all):
    '''
      연관성 분석 결과로 추천할 관광지 리스트 반환
      rules: 연관성 분석 결과
      act_wanted: 원하는 카테고리 리스트
      non_recmd: 추천받지 않을 카테고리 리스트
    '''
    
    rules_ = rules.copy()
    
    rules_['antecedents'] = rules_['antecedents'].apply(lambda x: set(x))
    rules_['consequents'] = rules_['consequents'].apply(lambda x: set(x))
    
    rules_ = rules_[rules_['consequents'].apply(lambda x: len(x.intersection(non_recmd))==0)]
    if sub_all == 'sub':
      return rules_[rules_['antecedents'].apply(lambda x: act_wanted.issubset(x))]
    if sub_all == 'all':
      return rules_[rules_['antecedents'].apply(lambda x: act_wanted == x)]

  def date_check(self, date):
    '''
      수요 예측 가능한 날짜가 입력되었는지 확인
      date: 수요 예측할 일자
    '''
    if date == None:
      return
    year = '2022' # 수요예측 가능한 년도
    month = '12' # 수요예측 가능한 월
    if type(date) != str:
      raise TypeError("문자열을 입력해주세요.")
      return
    if (date[:4] != year)| (date[4:6] != month) | (int(date[6:8]) not in range(2,31+1)):
      raise ValueError(f'{year}년 {month}월 2 ~ 31일에 해당하는 일자를 입력해주세요')
      return

  def recommend(self, act_wanted = [], date = None, answer = [], non_recmd=['자연','맛집_카페'], retry = False):
    ''' 
        선택한 카테고리 외 새로운 카테고리와 그에 속하는 관광지를 추천
        -> 이전에 경험하지 못한 색다른 경험을 위함
        act_wanted: 선택한 카테고리 리스트
        date: 날짜
        answer: 설문 결과
        non_recmd: 추천 받지 않을 카테고리 리스트
        retry: 재검색 여부

        act_wanted = [] # default
        date = None # default
        answer = [] # default
        non_recmd = ['자연','맛집_카페'] # default
        retry = False # default
        
        완전 추천: antecedents가 원하는 카테고리 리스트와 정확히 일치하는
        이것도 추천: antecedents에 원하는 카테고리 리스트가 속하는(부분집합)
    '''

    if act_wanted == []:
      if retry == False:
        return # '좋았거나 관심 있는 여행지를 하나 이상 선택해주세요'
      else:
        return None, None, None
    
    self.date_check(date)
    
    cluster_target = self.answer_to_clsuter(answer)
  
    act_wanted_list = list(act_wanted.copy())
    act_wanted = set(act_wanted)
    non_recmd = set(non_recmd)

    rules_target = self.rules_maker(self.senior[self.senior['cluster'].apply(lambda x: x in cluster_target)], self.cat_dic)
    
    recommend_sub = self.rule_to_rcd(rules_target, act_wanted, non_recmd, 'sub')
    recommend_all = self.rule_to_rcd(rules_target, act_wanted, non_recmd, 'all')

    new_cat = set()
    new_cat_spot = set()
    
    if len(recommend_all) != 0:
        new_cat = recommend_all["consequents"].iloc[0]
    elif len(recommend_sub) != 0:
        new_cat = recommend_sub["consequents"].iloc[0]

    if new_cat:
        new_cat_spot = self.recommend_spot(new_cat, self.spot)
        try:
          new_cat_spot_demand = self.rcd_demand(new_cat_spot, date, self.rcd_data)
          if not new_cat_spot_demand:
            new_cat_spot_demand = None
        except:
          new_cat_spot_demand = None

    else:
        new_cat, new_cat_spot, new_cat_spot_demand = self.recommend(act_wanted_list[:-1], date = date, answer=answer, non_recmd = non_recmd, retry = True)
    return new_cat, new_cat_spot, new_cat_spot_demand

  def recommend2(self, act_wanted = [], date = None, answer = [], non_recmd=['자연','맛집_카페']):
    ''' 
        선택한 카테고리의 관광지를 추천
        -> 기존의 추천 시스템과 동일
        date: 날짜
        answer: 설문 결과
        non_recmd: 추천 받지 않을 카테고리 리스트
  
        act_wanted = [] # default
        date = None # default
        answer = [] # default
        non_recmd = ['자연','맛집_카페'] # default
        
        완전 추천: antecedents가 원하는 카테고리 리스트와 정확히 일치하는
        이것도 추천: antecedents에 원하는 카테고리 리스트가 속하는(부분집합)
    '''
    
    if act_wanted == []:
      return # '좋았거나 관심 있는 여행지를 하나 이상 선택해주세요'
    
    self.date_check(date)

    cat_spot = self.recommend_spot(act_wanted, self.spot)
    
    try:
      cat_spot_demand = self.rcd_demand(cat_spot, date, self.rcd_data)
      if not cat_spot_demand:
        cat_spot_demand = None
    except:
      cat_spot_demand = None

    return cat_spot, cat_spot_demand
  def recommend_fin(self, act_wanted = [], date = None, answer = [], non_recmd=['자연','맛집_카페'], new = False):
    rc1 = self.recommend(act_wanted = act_wanted, date = date, answer = answer, non_recmd = non_recmd)
    rc2 = self.recommend2(act_wanted = act_wanted, date = date, answer = answer, non_recmd = non_recmd)
    rc3 = [None, None]
    if new == False:
      if rc1[1] != None:
        if rc2[0] != None:
          rc3[0] = rc2[0].union(rc1[1])
        else:
          rc3[0] = rc2[0]
      else:
        if rc2[0] != None:
          rc3[0] = rc3[0]
      
      if rc1[2] != None:
        if rc2[1] != None:
          rc3[1] = rc2[1].union(rc1[2])
        else:
          rc3[1] = rc2[1]
      else:
        if rc2[1] != None:
          rc3[1] = rc3[1]
      
    else:
      if rc1[1] != None:
        rc3[0] = rc1[1]
      else:
        rc3[0] = None

      if rc1[2] != None:
        rc3[1] = rc1[2]
      else:
        rc3[1] = None
      
    if rc3[0]:
        rc_spot = list(rc3[0])
        if rc3[1]:
          rc_spot_demand = list(rc3[1])
          
    return rc1[0], rc_spot, rc_spot_demand
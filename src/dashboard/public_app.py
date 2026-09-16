"""Public dashboard: bundled records are demonstration data, never live listings."""
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
from src.dashboard.team_workspace import workspace

ROOT = Path(__file__).resolve().parents[2]
PAGES = ['한눈에 보기', '직무교육 찾기', '지역별 교육 비교', '온라인 학습 분석', '교육과정 설계', '자료·분석 방법', '팀 자료실·분석실']
TITLE = '수도권 재교육 공동연구 대시보드'
COLORS = ['#087F8C', '#23395B', '#7196B5', '#DAA44B', '#856B9C']

@st.cache_data
def load_data():
    courses = pd.read_csv(ROOT / 'data/sample/kmooc_courses.csv', dtype={'matched_code': str})
    ncs = pd.read_csv(ROOT / 'data/sample/ncs_curriculums.csv', dtype={'job_code': str})
    stats = pd.read_csv(ROOT / 'data/sample/remote_learning_stats.csv')
    courses['광역지역'] = courses.region.str.split().str[0]
    return courses, ncs, stats

def filtered_courses(courses, regions, category, query):
    mask = courses['광역지역'].isin(regions)
    if category != '전체': mask &= courses.category.eq(category)
    if query.strip():
        mask &= (courses.course_title.str.contains(query.strip(), regex=False, case=False, na=False)
                 | courses.org_name.str.contains(query.strip(), regex=False, case=False, na=False))
    return courses.loc[mask].copy()

def public_table(courses):
    table = courses[['course_title','org_name','region','category','cost','weeks','weekly_hours']].rename(columns={
        'course_title':'강좌명(예시)','org_name':'기관명(예시)','region':'지역','category':'직무',
        'cost':'수강료(예시)','weeks':'주차(예시)','weekly_hours':'주당 시간(예시)'})
    table['모집·시간대·교육방식'] = '미확인'
    table['자료 구분'] = '시연용 샘플'
    return table

def download(frame, label, filename):
    st.download_button(label, frame.to_csv(index=False).encode('utf-8-sig'), filename, 'text/csv')

def chart(fig):
    fig.update_layout(font=dict(family='Malgun Gothic, sans-serif', color='#23395B'), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=8,r=8,t=45,b=8))
    st.plotly_chart(fig, use_container_width=True)

def navigate(page): st.session_state['page'] = page

def overview(courses, ncs):
    st.title('자료를 함께 살펴보고, 교육의 다음 방향을 찾습니다')
    st.write('수도권 5대 직무의 교육 자원을 탐색하고, 지역별 차이를 분석하며, 재직자를 위한 마이크로디그리 초안을 함께 검토하는 팀 연구 공간입니다.')
    st.button('팀 자료실·분석실 열기', on_click=navigate, args=(PAGES[6],), type='primary', use_container_width=True)
    a,b = st.columns(2)
    with a:
        st.subheader('나에게 맞는 교육 탐색')
        st.write('지역과 직무를 선택해 강좌 탐색 흐름을 체험하세요.')
        st.button('직무교육 찾기', on_click=navigate, args=(PAGES[1],), type='primary', use_container_width=True)
    with b:
        st.subheader('재직자를 위한 과정 설계')
        st.write('능력단위와 실습을 묶어 온·오프라인 교육과정 초안을 만드세요.')
        st.button('교육과정 설계하기', on_click=navigate, args=(PAGES[4],), use_container_width=True)
    st.divider()
    st.subheader('현재 체험할 수 있는 범위')
    a,b,c = st.columns(3)
    a.metric('강좌 예시', f'{len(courses)}개')
    b.metric('직무 분야', f'{courses.category.nunique()}개')
    c.metric('능력단위 예시', f'{len(ncs)}개')
    st.caption('실제 수집 건수와 산업 수요 지표가 아닙니다. 서울·경기 중심이며 기존 인천 예시도 포함합니다.')
    st.subheader('이 프로젝트가 답하려는 질문')
    st.markdown('1. 재직자가 참여할 수 있는 직무교육은 어느 지역·시간대에 부족할까요?\n2. 온라인 이론과 현장 실습은 어떻게 연결할 수 있을까요?\n3. NCS 기반 단기 교육과정을 지역 교육 자원과 어떻게 구성할까요?')
    st.info('현재 단계: 공개 시연 화면 구축 · 다음 단계: API 응답 검증 및 실제 자료 연결')

def explore(courses):
    st.title('직무교육 찾기')
    st.write('지역과 관심 직무로 강좌 예시를 좁혀보세요. 현재 목록은 실제 수강 신청용이 아닙니다.')
    a,b = st.columns(2)
    regions = a.multiselect('지역', sorted(courses['광역지역'].unique()), default=['서울','경기'])
    category = b.selectbox('관심 직무', ['전체'] + sorted(courses.category.unique()))
    query = st.text_input('강좌명 또는 기관명 검색', placeholder='예: 엑셀, 마케팅, 평생학습관')
    result = filtered_courses(courses, regions, category, query)
    st.caption('요일·시작 시간·모집 기간·교육 방식은 아직 확보되지 않아 필터를 제공하지 않습니다.')
    st.subheader(f'선택 조건에 맞는 예시 {len(result)}개')
    if result.empty: st.info('선택 조건에 맞는 예시가 없습니다. 지역을 추가하거나 검색어를 지워보세요.')
    else:
        st.dataframe(public_table(result), hide_index=True, use_container_width=True)
        download(public_table(result), '선택한 강좌 예시 내려받기', 'demo_courses.csv')
    st.markdown('실제 개설 정보는 [K-MOOC](https://www.kmooc.kr/) 등 제공기관에서 확인하세요. 예시 강좌에 대응하는 신청 링크는 아직 없습니다.')

def compare(courses):
    st.title('지역별 교육 비교')
    st.write('같은 직무의 교육 자원이 지역별로 어떻게 분포하는지 살펴보는 시연입니다.')
    category = st.selectbox('비교할 직무', ['전체'] + sorted(courses.category.unique()))
    data = courses if category == '전체' else courses[courses.category == category]
    counts = data.groupby(['광역지역','category']).size().reset_index(name='강좌 예시 수')
    chart(px.bar(counts, x='광역지역', y='강좌 예시 수', color='category', barmode='group', color_discrete_sequence=COLORS, labels={'category':'직무'}, title='샘플에 포함된 지역별 강좌 구성'))
    st.warning('샘플 수의 차이를 지역의 실제 교육 격차로 해석할 수 없습니다. 미수집 지역은 강좌가 없는 지역이 아닙니다.')
    st.subheader('야간·주말 교육 접근성')
    st.info('분석 대기: 강의 요일과 시작·종료 시간이 필요합니다. 현재 자료로는 야간·주말 비율을 계산하지 않습니다.')
    with st.expander('실제 자료 연결 후 적용할 계산 기준'):
        st.write('야간은 평일 18시 이후 시작하는 강좌, 주말은 토·일 운영 강좌로 정의합니다. 두 조건을 모두 충족하는 강좌는 한 번만 셉니다.')
        st.write('야간·주말 비율 = 해당 강좌 수 ÷ 시간대 판정이 가능한 강좌 수. 미확인 건수와 시간대 정보 확보율을 함께 공개합니다.')
        st.write('지역별 단순 강좌 수는 수집 범위와 인구 규모의 영향을 받습니다. 전체 지역 수집과 인구 자료 확보 후 인구 대비 지표를 별도로 제공합니다.')
    download(counts.assign(자료구분='시연용 샘플'), '비교표 내려받기', 'demo_region_comparison.csv')

def online(stats):
    st.title('온라인 학습 분석')
    st.info('실제 분석 결과는 아직 없습니다. 영상 길이·평가 유무·수강 및 수료 인원의 제공 여부를 확인해야 합니다.')
    with st.expander('시연용 원격훈련 그래프 보기'):
        chart(px.line(stats, x='total_hours', y='completion_rate', color='target_group', markers=True, color_discrete_sequence=COLORS, labels={'total_hours':'총시간(예시)','completion_rate':'수료율(예시, %)','target_group':'대상(예시)'}, title='합성 샘플: 시간별 수료율 표시 예시'))
        st.caption('공식 통계가 아닙니다. 이 그래프로 40시간 이탈 임계선이나 최적 교육시간을 주장할 수 없습니다.')
    st.subheader('검증할 가설과 필요한 자료')
    st.table(pd.DataFrame([
        ['짧은 영상과 수료율의 관계','차시별 러닝타임, 강좌별 수료율','추가 확보 필요'],
        ['퀴즈 제공과 수료율의 관계','평가 구성, 난이도, 대상자, 수료율','추가 확보 필요'],
        ['직무별 원격훈련 수료 현황','동일 기준의 수강 인원·수료 인원','응답 검증 필요'],
    ], columns=['분석 질문','필요한 자료','상태']))
    st.write('수료율은 동일 기간·집단의 수료 인원을 수강 인원으로 나누어 계산합니다. 집계 시 분모를 반영하며 K-MOOC와 직업훈련 통계는 구분합니다. 회귀분석에서 관찰되는 관계만으로 인과효과를 단정하지 않습니다.')

def build_curriculum(ncs, category, units, total, ratio):
    rows = ncs[(ncs.category == category) & ncs.unit_name.isin(units)]
    online_hours = round(total * ratio / 100, 1)
    return pd.DataFrame([{'과정명':f'{category} 마이크로디그리 설계 초안','총시간':total,'온라인시간':online_hours,'오프라인시간':round(total-online_hours,1),
        '능력단위(예시)':' / '.join(rows.unit_name),'직무코드(예시)':' / '.join(rows.job_code),'실습과제(예시)':' / '.join(rows.offline_practice),
        '자료구분':'시연용 샘플 기반 설계','인정여부':'학점·학위·자격 인정은 운영기관 확인 필요'}])

def designer(ncs):
    st.title('교육과정 설계')
    st.write('온라인 이론과 오프라인 실습을 조합해 재직자 맞춤형 과정의 초안을 만들어보세요.')
    category = st.selectbox('설계할 직무', sorted(ncs.category.unique()))
    subset = ncs[ncs.category == category]
    units = st.multiselect('포함할 능력단위 예시', subset.unit_name.tolist(), default=subset.unit_name.tolist())
    a,b = st.columns(2)
    total = a.slider('총 교육시간',20,80,40,5)
    ratio = b.slider('온라인 비율 (%)',0,100,60,5)
    st.caption('40시간·온라인 60%는 조정 가능한 초기 가정입니다. 검증된 최적값이나 학점 기준이 아닙니다.')
    if not units:
        st.info('능력단위를 하나 이상 선택하면 초안을 만들 수 있습니다.')
        return
    plan = build_curriculum(ncs, category, units, total, ratio)
    a,b,c = st.columns(3)
    a.metric('총 교육시간', f'{total}시간')
    b.metric('온라인 이론', f'{plan.iloc[0]["온라인시간"]:g}시간')
    c.metric('오프라인 실습', f'{plan.iloc[0]["오프라인시간"]:g}시간')
    st.subheader('선택한 학습 내용')
    st.dataframe(subset[subset.unit_name.isin(units)][['unit_name','offline_practice']].rename(columns={'unit_name':'능력단위 예시','offline_practice':'실습과제 예시'}), hide_index=True, use_container_width=True)
    st.write('운영 제안: 온라인은 평일 자율학습, 실습은 주말 집체교육으로 편성할 수 있습니다. 실제 일정과 단위별 시간은 운영기관이 조정해야 합니다.')
    st.warning('자동 생성 결과는 설계 초안입니다. 대학 개설 승인, 학점·학위·자격 인정, 강사·공간 확보를 보장하지 않습니다.')
    download(plan, '교육과정 초안 내려받기', 'demo_microdegree_draft.csv')

def methods(courses):
    st.title('자료·분석 방법')
    st.write('수도권 산업 수요 기반 산학 연계형 마이크로디그리 설계 및 하이브리드 재교육 모델 개발')
    st.markdown('[프로젝트 GitHub 및 문서](https://github.com/kimsaemi/edu-skill-gap)')
    st.subheader('데이터 확보 현황')
    st.table(pd.DataFrame([
        ['서울·경기 평생학습','지역·강좌·요일·시간','실제 응답 검증 필요'],
        ['K-MOOC','강좌 정보·영상·평가·수료','세부 항목 제공 여부 확인 필요'],
        ['원격훈련 모니터링','수강·수료 인원','실제 통계 연결 필요'],
        ['NCS 교육과정','코드·능력단위·시간','공식 정보 대조 필요'],
        ['고용24','훈련과정·직무 키워드','추가 예정'],
    ],columns=['자료','수집 목표','상태']))
    st.caption('수집 기준일: 미확인 · 마지막 API 수집 성공: 미검증 · 현재 화면은 저장소의 샘플 CSV만 사용합니다.')
    st.subheader('해석할 때 알아둘 점')
    st.markdown('- 산업 수요 점수는 공개 지표에서 제외했습니다. 훈련 공급을 산업 수요로 해석하려면 채용·기업 조사 자료가 추가로 필요합니다.\n- 강좌의 기간·모집 상태·시간대·교육 방식·원문 URL은 현재 샘플에서 확인할 수 없습니다.\n- 기관명과 학점 인정 문구가 포함된 원본도 예시입니다. 공개 탐색 목록에서는 학점 인정 문구를 제외했습니다.\n- NCS 코드와 능력단위 매핑은 예시이며 공식 표준과 대조가 필요합니다.')
    with st.expander('강좌 데이터 사전'):
        st.table(pd.DataFrame([
            ['강좌명·기관명','샘플 강좌와 기관 표시','실제 개설 확인 전'],
            ['지역','샘플의 기관 소재지','온라인 수강 가능 지역과 다를 수 있음'],
            ['직무','프로젝트의 5대 직무 분류','매핑 검토 필요'],
            ['주차·주당 시간','예시 과정의 학습 분량','요일·시작 시간을 의미하지 않음'],
        ],columns=['항목','정의','주의점']))
    download(public_table(courses), '전체 강좌 예시 내려받기', 'demo_all_courses.csv')
    st.subheader('발표에 활용하기')
    st.write('문제 제기 → 지역별 교육 비교 → 온라인 분석에 필요한 근거 → 교육과정 설계 시연 순으로 설명하세요. 시연 데이터라는 전제를 유지하고 실제 연구 결과와 구분하세요.')

def main():
    st.set_page_config(page_title=TITLE,page_icon='🎓',layout='wide')
    st.markdown('''<style>
    .stApp {background:#F5F8FB;color:#23395B;}
    [data-testid="stSidebar"] {background:#E8EFF4;}
    h1,h2,h3 {color:#23395B;letter-spacing:-.035em;}
    h1 {max-width:900px;line-height:1.2!important;}
    .block-container {max-width:1180px;padding-top:2.2rem;}
    [data-testid="stMetricValue"] {color:#087F8C;}
    .stButton button {min-height:48px;}
    </style>''',unsafe_allow_html=True)
    courses,ncs,stats = load_data()
    with st.sidebar:
        st.header('수도권 직무교육')
        st.caption('자료 탐색 · 비교 분석 · 연구 기록')
        page = st.radio('메뉴',PAGES,key='page')
        st.divider()
        st.caption('팀 공동연구 공간 · 샘플/업로드 자료')
        st.caption('서울·경기 중심 / 인천 예시 포함')
    if page != PAGES[6]:
        st.warning('기본 자료는 시연용입니다. 실제 개설·모집·학점 인정 정보나 수도권 전체 현황을 나타내지 않습니다.')
    if page == PAGES[0]: overview(courses,ncs)
    elif page == PAGES[1]: explore(courses)
    elif page == PAGES[2]: compare(courses)
    elif page == PAGES[3]: online(stats)
    elif page == PAGES[4]: designer(ncs)
    elif page == PAGES[5]: methods(courses)
    else: workspace(ROOT)
    st.divider()
    st.caption('수도권 직무교육 탐색·설계 | 출처와 한계는 자료·분석 방법에서 확인하세요.')


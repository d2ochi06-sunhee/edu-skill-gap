from streamlit.testing.v1 import AppTest
from src.dashboard.public_app import load_data, filtered_courses, build_curriculum, PAGES
courses, ncs, _ = load_data()
assert filtered_courses(courses, [], '전체', '').empty
assert filtered_courses(courses, ['서울','경기'], '전체', '[').empty
for category in ncs.category.unique():
    units = ncs[ncs.category == category].unit_name.tolist()
    for ratio in [0, 35, 60, 100]:
        p = build_curriculum(ncs, category, units, 45, ratio).iloc[0]
        assert abs(p['온라인시간'] + p['오프라인시간'] - 45) < 1e-8
app = AppTest.from_file(str(__import__('pathlib').Path(__file__).resolve().parents[1] / 'app.py')).run(timeout=30)
assert not app.exception, app.exception
app.button[1].click().run()
assert app.radio[0].value == PAGES[1]
app.multiselect[0].set_value([]).run()
assert not app.exception
for page in PAGES:
    app.radio[0].set_value(page).run(timeout=30)
    assert not app.exception, (page, app.exception)
app.radio[0].set_value(PAGES[4]).run()
app.slider[1].set_value(100).run()
assert not app.exception
app.multiselect[0].set_value([]).run()
assert not app.exception
other = AppTest.from_file(str(__import__('pathlib').Path(__file__).resolve().parents[1] / 'src/dashboard/app.py')).run(timeout=30)
assert not other.exception
print('PASS: six pages, navigation, empty filters, literal search, curriculum totals and both entry points')



# Team workspace: decoding, identifiers, missing numeric values, aggregation and UI.
import pandas as pd
from src.dashboard.team_workspace import parse_csv, quality_table, summarize
f = parse_csv('code,group,value\n001,A,10\n002,A,20\n003,B,bad\n004,,30\n'.encode(), 'utf-8-sig')
assert f.code.iloc[0] == '001'
r, excluded = summarize(f, 'group', 'value', '평균')
assert excluded == 1
assert r.loc[r['group']=='A', 'value · 평균'].iloc[0] == 15
assert r.loc[r['group']=='미확인', 'value · 평균'].iloc[0] == 30
assert quality_table(f).loc[lambda x: x['항목']=='group','결측 건수'].iloc[0] == 1
r, excluded = summarize(f.iloc[:0], 'group', 'value', '평균')
assert r.empty
app.radio[0].set_value(PAGES[6]).run()
assert not app.exception
# Source changes must remain valid for unrelated column schemas.
for source in ['강좌 통합 샘플', 'NCS 교육과정 샘플', '원격훈련 통계 샘플']:
    app.selectbox[0].set_value(source).run()
    assert not app.exception
    op = next(x for x in app.selectbox if x.label == '계산 방식')
    op.set_value('평균').run()
    assert not app.exception
app.selectbox[0].set_value('CSV 업로드').run()
assert not app.exception
print('PASS: team workspace sources, CSV leading zeros, missing groups, numeric exclusions, means and empty data')

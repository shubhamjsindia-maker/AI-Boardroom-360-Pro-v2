import unittest
from core.demo import sample_company
from core.financial import validate_dataset,validate,ratios
from core.importer import make_template,read_workbook

class FinanceTests(unittest.TestCase):
    def setUp(self):self.data=sample_company()
    def test_sample_valid(self):self.assertEqual(validate_dataset(self.data),[])
    def test_five_years(self):self.assertEqual(len(self.data['periods']),5)
    def test_bad_balance_sheet(self):
        p=self.data['periods']['FY2026'].copy();p['total_assets']='999';self.assertTrue(any(x['rule']=='BS-03' for x in validate(p)))
    def test_missing_never_zero(self):
        p=self.data['periods']['FY2026'].copy();p.pop('revenue');self.assertTrue(any(x['rule']=='DATA' for x in validate(p)))
    def test_ratio(self):self.assertGreater(ratios(self.data['periods']['FY2026'])['EBITDA Margin (%)'],0)
    def test_template_roundtrip(self):
        result,errors=read_workbook(make_template(self.data))
        self.assertEqual(errors,[]);self.assertEqual(str(result['periods']['FY2026']['revenue']),str(self.data['periods']['FY2026']['revenue']))
        self.assertEqual(len(result['periods']),5)
    def test_multiple_years(self):
        for n in (2,3,4,5):
            d=dict(self.data,periods=dict(list(self.data['periods'].items())[-n:]));self.assertEqual(validate_dataset(d),[])
    def test_one_year_rejected(self):
        d=dict(self.data,periods={'FY2026':self.data['periods']['FY2026']});self.assertTrue(validate_dataset(d))

if __name__=='__main__':unittest.main()

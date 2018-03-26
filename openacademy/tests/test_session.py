from odoo.tests import common
# from unittest2 import SkipIf

class TestSession(common.TransactionCase):

    def setUp(self):
        super(TestSession, self).setUp()

    def tearDown(self):
        super(TestSession, self).tearDown()

    def test_check_percentage_change(self):
        #check initial percentage

        initial_session = self.env.ref('openacademy.session_1')
        initial_prc = initial_session.taken_seats

        partner = self.env.ref('base.res_partner_1')

        #change number of attendess in a session
        initial_session.write({'attendee_ids': [(4, partner.id)]})
        #check if percentage is different
        final_prc = initial_session.taken_seats
        self.assertNotEqual(initial_prc, final_prc, 'The percentage of seats taken didn\'t change after a change of number of attendes (inc by 1)')

    def test_end_date_change(self):
        #chek initial end date
        initial_session_rs = self.env.ref('openacademy.session_1')
        initial_end_date = initial_session_rs.end_date
        #change duration and see if end date changes
        initial_session_rs.write({'duration': 24})
        after_dur_change_end_date = initial_session_rs.end_date
        self.assertNotEqual(initial_end_date, after_dur_change_end_date, 'Session end date didn\'t change after a duration change')
        #revert to initial end date
        initial_session_rs.write({'end_date': initial_end_date})
        #change start date and see if end date changes
        initial_session_rs.write({'start_date': '2018-03-15 01:00:00'})
        after_stdate_change_end_date = initial_session_rs.end_date
        self.assertNotEqual(initial_end_date, after_stdate_change_end_date,
                            'Session end date didn\'t change after a duration change')
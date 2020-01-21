from odoo.tests import common
from datetime import date
from dateutil.relativedelta import relativedelta

class TestSession(common.TransactionCase):

    def test_inverse_duration(self):

        session = self.env['session'].create({
            'name': 'Test session',
            'duration': 0,
            'start_date': date.today(),
            'end_date': date.today() + relativedelta(days=5)
        })

        context = {"active_model": 'session', "active_ids": [session.id], "active_id": session.id}
        session.with_context(context)._inverse_duration()

        self.assertEqual(session.duration, 5)

    def test_register_attendees(self):

        attendee_1 = self.env['res.partner'].create({
            'name': 'First Attendee'
        })
        attendee_2 = self.env['res.partner'].create({
            'name': 'Second Attendee'
        })
        first_session = self.env['session'].create({
            'name': 'Test session 1',
            'attendees': [attendee_2.id]
        })
        second_session = self.env['session'].create({
            'name': 'Test session 2',
            'attendees': []
        })
        wizard = self.env['wizard'].create({
            'session_ids': [first_session.id, second_session.id],
            'attendees': [attendee_1.id, attendee_2.id]
        })
        context = {"active_model": 'wizard', "active_ids": [wizard.id], "active_id": wizard.id}
        wizard.with_context(context).register_attendees()

        result_session_1 = first_session.attendees | wizard.attendees
        result_session_2 = second_session.attendees | wizard.attendees

        self.assertEqual(first_session.attendees, result_session_1)
        self.assertEqual(second_session.attendees, result_session_2)




from flask_testing import TestCase
from app import *
from app.extensions import db


class BaseTestCase(TestCase):
    def create_app(self):
        app = create_app()
        app.config.update({
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db',
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'TESTING': True
        })
        db.init_app(app)
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


james = User(first_name='James', last_name='Paul', email='jamespaul8967@gmail.com', phone='+19493003417', password='123', location1='Doheny State Beach', loc1_lat=33.460304, loc1_lon=242.314139, location2='T-Street San Clemente', loc2_lat=33.416018, loc2_lon=242.381431, location3='San Onofre State Beach', loc3_lat=33.374922, loc3_lon=242.429478, notif_time='1:35 PM')
#ambika = User(first_name='Ambika', last_name='Mathur', email='ambikamathur9@gmail.com', phone='+19493575418', password='12345', location1='Doheny State Beach', loc1_lat=33.460304, loc1_lon=-117.685861, location2='T-Street San Clemente', loc2_lat=33.416018, loc2_lon=-117.618569, location3='San Onofre State Beach', loc3_lat=33.374922, loc3_lon=-117.570522, notif_time='8:00 AM')
doheny = Locations(location_name='Doheny State Beach', loc_lat=33.460304, loc_lon=242.314139, tolerance=0.25)
t_street = Locations(location_name='T-Street', loc_lat=33.416018, loc_lon=242.381431, tolerance=0.25)
san_o = Locations(location_name='San Onofre State Beach', loc_lat=33.374922, loc_lon=242.429478, tolerance=0.25)

class TestApp(BaseTestCase):

    def _add_to_db(self, record):
        db.session.add(record)
        db.session.commit()
    
    def test_first(self):
        
        self._add_to_db(james)
        #self._add_to_db(ambika)
        self._add_to_db(doheny)
        self._add_to_db(t_street)
        self._add_to_db(san_o)
        update_surf_data(today='20210308', hour='00')
        send_texts()



if __name__ == '__main__':
    import unittest
    unittest.main()
BUILDING_CODE_CHOICES = [
    ('2021IBC', '2021 IBC'),
    ('2018IBC', '2018 IBC'),
    ('2015IBC', '2015 IBC'),
    ('2012IBC', '2012 IBC'),
    ('2009IBC', '2009 IBC'),
    ('NoSolarRegulations', 'No Solar Regulations')
]

ELECTRIC_CODE_CHOICES = [
    ('2020NEC', '2020 NEC'),
    ('2017NEC', '2017 NEC'),
    ('2014NEC', '2014 NEC'),
    ('2011NEC', '2011 NEC'),
    ('NoSolarRegulations', 'No Solar Regulations')
]

FIRE_CODE_CHOICES = [
    ('2021IFC', '2021 IFC'),
    ('2018IFC', '2018 IFC'),
    ('2015IFC', '2015 IFC'),
    ('2012IFC', '2012 IFC'),
    ('2009IFC', '2009 IFC'),
    ('NoSolarRegulations', 'No Solar Regulations')
]

RESIDENTIAL_CODE_CHOICES = [
    ('2021IRC', '2021 IRC'),
    ('2018IRC', '2018 IRC'),
    ('2015IRC', '2015 IRC'),
    ('2012IRC', '2012 IRC'),
    ('2009IRC', '2009 IRC'),
    ('NoSolarRegulations', 'No Solar Regulations')
]

WIND_CODE_CHOICES = [
    ('ASCE716', 'ASCE7-16'),
    ('ASCE710', 'ASCE7-10'),
    ('ASCE705', 'ASCE7-05'),
    ('SpecialWindZone', 'Special Wind Zone')
]

DOCUMENT_SUBMISSION_METHOD_CHOICES = [
    ('Epermitting', 'Epermitting'),
    ('Email', 'Email'),
    ('InPerson', 'In Person'),
    ('SolarApp', 'SolarAPP')
]

PERMIT_ISSUE_METHOD_CHOICES = [
    ('Epermitting', 'Epermitting'),
    ('Email', 'Email'),
    ('InPerson', 'In Person'),
    ('SolarApp', 'SolarAPP')
]

ADDRESS_TYPE_CHOICES = [
    ('Mailing', 'Mailing'),
    ('Billing', 'Billing'),
    ('Installation', 'Installation'),
    ('Shipping', 'Shipping')
]

LOCATION_DETERMINATION_METHOD_CHOICES = [
    ('GPS', 'GPS'),
    ('Survey', 'Survey'),
    ('AerialImage', 'Aerial Image'),
    ('EngineeringReport', 'Engineering Report'),
    ('AddressGeocoding', 'Address Geocoding'),
    ('Unknown', 'Unknown')
]

LOCATION_TYPE_CHOICES = [
    ('DeviceSpecific', 'Device Specific'),
    ('SiteEntrance', 'Site Entrance'),
    ('GeneralProximity', 'General Proximity'),
    ('Warehouse', 'Warehouse')
]

CONTACT_TYPE_CHOICES = [
    ('Homeowner', 'Homeowner'),
    ('OffTaker', 'Off Taker'),
    ('Inspector', 'Inspector'),
    ('Engineer', 'Engineer'),
    ('Originator', 'Originator'),
    ('Installer', 'Installer'),
    ('Investor', 'Investor'),
    ('PermittingOfficial', 'Permitting Official'),
    ('FireMarshal', 'Fire Marshal'),
    ('ProjectManager', 'Project Manager'),
    ('Salesperson', 'Salesperson')
]

PREFERRED_CONTACT_METHOD_CHOICES = [
    ('Email', 'Email'),
    ('WorkPhone', 'Work Phone'),
    ('CellPhone', 'Cell Phone'),
    ('HomePhone', 'Home Phone'),
    ('CellTextMessage', 'Cell Text Message'),
]

ENGINEERING_REVIEW_TYPE_CHOICES = [
    ('StructuralEngineer', 'Structural Engineer'),
    ('ElectricalEngineer', 'Electrical Engineer'),
    ('PVEngineer', 'PV Engineer'),
    ('MasterElectrician', 'Master Electrician'),
    ('FireMarshal', 'Fire Marshal'),
    ('EnvironmentalEngineer', 'Environmental Engineer')
]

REQUIREMENT_LEVEL_CHOICES = [
    ('Required', 'Required'),
    ('Optional', 'Optional'),
    ('ConditionallyRequired', 'Conditionally Required')
]

STAMP_TYPE_CHOICES = [
    ('Wet', 'Wet'),
    ('Digital', 'Digital'),
    ('Notary', 'Notary'),
    ('None', 'None')
]

FEE_STRUCTURE_TYPE_CHOICES = [
    ('Flat', 'Flat'),
    ('SystemSize', 'System Size')
]

INSPECTION_TYPE_CHOICES = [
    ('RoughIn', 'Rough In'),
    ('Final', 'Final'),
    ('Windstorm', 'Windstorm'),
    ('Electrical', 'Electrical'),
    ('Structural', 'Structural')
]

FIELD_VALIDATION = {
    'Location': {
        'Longitude': lambda value: -180 <= float(value) <= 180,
        'Latitude': lambda value: -90 <= float(value) <= 90
    }
}

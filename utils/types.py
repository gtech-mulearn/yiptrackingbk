from enum import Enum

class Role(Enum):
    ADMIN = 'Admin'
    INTERN = 'Intern'
    DISTRICT_COORDINATOR = 'District Coordinator'
    ZONE_COORDINATOR = 'Zone Coordinator'

    @classmethod
    def choices(cls):
        return [key.name for key in cls]
    
    @classmethod
    def get_role(cls, role):
        vals =  [key.value for key in cls if key.value == role]
        return vals[0] if len(vals) == 1 else None

class OrgType(Enum):
    COLLEGE = 'College'
    SCHOOL = 'School'
    ITI = 'Iti'
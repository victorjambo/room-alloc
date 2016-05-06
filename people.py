import random
from db.dbManager import DBManager
from rooms import Rooms, LivingSpace, OfficeSpace
from pprint import pprint as pp

class Person:
    def __init__(self):
        self.db = DBManager('room_alloc.db')

    def set_name(self, first_name, last_name):
        self.name = first_name + ' ' + last_name

    def unallocated(self, args):
        unallocated_fellows = Fellow().unallocated()
        unallocated_staff = Staff().unallocated()

        output = ''
        output += '*' * 30 + "\nSTAFF\n" + '*' * 30 + "\n"
        if unallocated_staff and len(unallocated_staff) != 0:
            output += ", ".join([str(i[1]) for i in unallocated_staff])
        else:
            output += 'All staff have been assigned'

        output += '\n\n' + '*' * 30 + "\nFELLOWS\n" + '*' * 30 + "\n"
        if unallocated_fellows and len(unallocated_fellows) != 0:
            output += "\n".join([str(i[1]) for i in unallocated_fellows])
        else:
            output += 'All fellows have been assigned'

        print(output)
        if args['--o'] is not None:
            with open('unallocated.txt', 'wt') as f:
                f.write(output)
                print "Unallocated people printed out to %s" % ('unallocated.txt')

class Staff(Person):
    def __init__(self):
        self.db = DBManager('room_alloc.db')

    def add_staff(self, args):
        """Add a new staff member to the system"""

        self.person = Person()
        self.person.set_name(args['<first_name>'], args['<last_name>'])

        """add a new staff to the system"""
        office_spaces = OfficeSpace().office_spaces()
        office_spaces = [i for i in office_spaces if i[-1] < OfficeSpace.room_space]
        if len(office_spaces) != 0:
            office_space = random.choice(office_spaces)
            new_staff = "INSERT INTO staff(name, room_id) VALUES ('%s', %d)" % (self.person.name, office_space[0])

            staff_id = self.db.insert(new_staff)

            if staff_id:
                print("New Staff succesfully added. Staff ID is %d" % (staff_id))
                print('%s office space is in %s.' % (self.person.name, office_space[1]))
            else:
                print("Error adding new staff. Please try again")
        else:
            print("There are no vacant office spaces. Please check in later")


    def reallocate(self, args):
        """Reallocate a staff member to a new office space"""

        staff_id = int(args['<person_identifier>'])
        staff = self.db.select_one("SELECT * FROM staff WHERE id = %d"% (staff_id))

        if staff:
            old_room = self.db.select_one("SELECT * FROM rooms WHERE id = %d AND type='O'" % (staff[-1]))
            new_room_name = args['<new_room_name>']

            if old_room[1] != new_room_name:
                office = OfficeSpace()
                new_room = office.office_space(new_room_name)

                if new_room:
                    room_occupancy = office.office_space_occupancy(new_room[0])
                    if len(room_occupancy) < office.room_space:
                        if office.allocate_room(staff_id, new_room[0]):
                            print("%s is now residing in %s" % (staff[1], new_room_name))
                    else:
                        print("%s is already fully occupied. Please try another room" % (new_room_name))
                else:
                    print("No office space by that name. Please try again")
            else:
                print("%s already belongs in %s" % (staff[1], new_room_name))
        else:
            print("No staff by the provided staff id '%d'" % staff_id)

    def unallocated(self):
        """Return a list of unallocated staff"""
        unallocated = self.db.select("SELECT * FROM staff WHERE room_id is NULL or room_id = ''")

        if unallocated:
            return unallocated
        return False


class Fellow(Person):
    def __init__(self):
        self.db = DBManager('room_alloc.db')

    def add_fellow(self, args):
        """Add a new fellow to the system"""

        self.person = Person()
        self.person.set_name(args['<first_name>'], args['<last_name>'])
        self.accomodation  = 'Y' if args['--a'] is not None and args['--a'].lower() == 'y' else 'N'
        new_fellow_query = "INSERT INTO fellows(name, accomodation) VALUES('{name}', '{accomodation}')".format(name = self.person.name, accomodation =  self.accomodation)

        fellow_id = self.db.insert(new_fellow_query)

        if fellow_id:
            print("New fellow succesfully added. Fellow ID is %d" % (fellow_id))
            if self.accomodation == 'Y':
                print('Searching for accomodation for the fellow...')
                self.accomodate_fellow(fellow_id)
            else:
                print('accomodation not provided for fellow.')
        else:
            print("Error adding new fellow. Please try again")

    def accomodate_fellow(self, fellow_id):
        """Accomodate a new fellow in the living spaces"""

        vacant_living_spaces = LivingSpace().living_spaces()
        vacant_living_spaces = [i for i in vacant_living_spaces if i[-1] < LivingSpace.room_space]
        if len(vacant_living_spaces) != 0:
            living_space = random.choice(vacant_living_spaces)
            query = "UPDATE fellows SET room_id = %d WHERE id = %d" % (living_space[0], fellow_id)
            if self.db.update(query):
                print("{} is now accommodated in {}".format(self.person.name, living_space[1]))
            else:
                print("Error acomomdating {}".format(self.person.name))
        else:
            print("There are no vacant living spaces for now. Please check in later")

    def reallocate(self, args):
        """Reallocate an existing fellow to a new room"""

        fellow_id = int(args['<person_identifier>'])
        fellow = self.db.select_one("SELECT * FROM fellows WHERE id = %d"% (fellow_id))
        if fellow:
            if fellow[2] == 'N':
                accommodate = raw_input("%s has opted out of amity accomodation.Would you like to proceed and accomodate the fellow? [y/n]" % (fellow[1]))
                if accommodate.upper() == 'Y':
                    self.allocate_new_fellow(fellow, fellow_id, args)
                else:
                    print("%s has not been allocated into any room." % format(fellow[1]))
            else:
                self.reallocate_fellow(fellow, fellow_id, args)
        else:
            print("No fellow by the provided fellow id '%d'" % fellow_id)

    def reallocate_fellow(self, fellow, fellow_id, args):
        old_room = self.db.select_one("SELECT * FROM rooms WHERE id = %d AND type='L'" % (fellow[-1]))
        new_room_name = args['<new_room_name>']
        if old_room[1] != new_room_name:
            living = LivingSpace()
            new_room = living.living_space(new_room_name)
            if new_room:
                room_occupancy = living.living_space_occupancy(new_room[0])
                if len(room_occupancy) < living.room_space:
                    if living.allocate_room(fellow_id, new_room[0]):
                        print("%s is now residing in %s" % (fellow[1], new_room_name))
                else:
                    print("%s is already fully occupied. Please try another room" % (new_room_name))
            else:
                print("No living space by that name. Please try again")
        else:
            print("%s already belongs in %s" % (fellow[1], new_room_name))

    def allocate_new_fellow(self, fellow, fellow_id, args):
        new_room_name = args['<new_room_name>']
        living = LivingSpace()
        new_room = living.living_space(new_room_name)
        if new_room:
            room_occupancy = living.living_space_occupancy(new_room[0])
            if len(room_occupancy) < living.room_space:
                if living.allocate_room(fellow_id, new_room[0]):
                    print("%s is now residing in %s" % (fellow[1], new_room_name))
            else:
                print("%s is already fully occupied. Please try another room" % (new_room_name))
        else:
            print("No living space by that name. Please try again")

    def unallocated(self):
        """Return a list of unallocated fellow"""
        unallocated = self.db.select("SELECT * FROM  fellows WHERE room_id is NULL or room_id = ''")

        if unallocated:
            return unallocated
        return False



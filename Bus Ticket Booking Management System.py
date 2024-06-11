import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

bus = [
    {"busName": "PS Travels", "availableTickets": 30, "destination": "chennai"},
    {"busName": "MS Travels", "availableTickets": 30, "destination": "bangalore"},
    {"busName": "SR Travels", "availableTickets": 30, "destination": "delhi"}
]

booking_details = []


class Ticket:
    def __init__(self):
        print("1. Booking")
        print("2. Exit")
        self.choice = int(input('Enter your choice : '))
        if self.choice == 1:
            self.booking_menu()
        else:
            exit()

    def booking_menu(self):
        print("1. Bus")
        print("2. Back")
        print("3. Exit")
        self.choice = int(input('Enter your choice : '))
        if self.choice == 1:
            self.bus_booking_menus()
        elif self.choice == 2:
            self.__init__()
        else:
            exit()

    def bus_booking_menus(self):
        print("1. Book Ticket")
        print("2. Cancel Ticket")
        print("3. Back")
        print("4. Exit")
        self.choice = int(input('Enter your choice : '))

        if self.choice == 1:
            self.bus_booking()
        elif self.choice == 2:
            self.cancel_booking()
        elif self.choice == 3:
            self.booking_menu()
        else:
            exit()

    def bus_booking(self):
        self.name = input("Enter your name: ")
        self.email = input("Enter your email: ")
        self.destiantion = input("Enter your destination: ")
        for b in bus:
            if self.destiantion == b['destination']:
                print(f"Following {b['busName']} and available ticket is {b['availableTickets']}")
                self.no_of_tickets = int(input("How many tickets you want: "))
                if self.no_of_tickets <= b['availableTickets']:
                    b['availableTickets'] -= self.no_of_tickets
                    print(b['availableTickets'])
                    print(f"Hi {self.name}, you booked {self.no_of_tickets} tickets.")
                    booking_details.append(
                        {"name": self.name, "destination": self.destiantion,"email":self.email, "numberOfTickets": self.no_of_tickets,
                         "busName": b['busName']})
                    confirmation_subject = "Booking Confirmation"
                    confirmation_body = f"Hi {self.name}, you have successfully booked {self.no_of_tickets} tickets for {b['busName']} to {self.destiantion}."
                    self.send_email(self.email, confirmation_subject, confirmation_body)
                elif self.no_of_tickets > b['availableTickets']:
                    print("Sorry! No more tickets are available, Please enter the ticket less than or equal to",
                          b['availableTickets'])
            else:
                print("Travels Not Available for that destination.")
        print(booking_details)
        self.bus_booking_menus()

    def cancel_booking(self):
        self.name = input("Enter your name: ")
        self.email = input("Enter your email: ")

        found_booking = False  
        for i in booking_details:
            if i["name"] == self.name:
                found_booking = True
                print(f"You booked {i['numberOfTickets']} tickets in {i['busName']}.")
                self.cancel_ticket = int(input("How many tickets you want to cancel: "))
                if self.cancel_ticket <= i["numberOfTickets"]:
                    remaining_tickets = i["numberOfTickets"] - self.cancel_ticket
                    i["numberOfTickets"] = remaining_tickets
                    print(
                        f"{self.cancel_ticket} tickets have been canceled, Your remaining tickets are {remaining_tickets}.")
                    for j in bus:
                        if j["busName"] == i["busName"]:
                            j['availableTickets'] += self.cancel_ticket
                            print(
                                f"Following {j['busName']} tickets are updated. Available Tickets: {j['availableTickets']}")
                    cancellation_subject = "Booking Cancellation"
                    cancellation_body = f"Hi {self.name}, you have successfully canceled {self.cancel_ticket} tickets for {i['busName']}. Your remaining tickets are {remaining_tickets}."
                    self.send_email(self.email, cancellation_subject, cancellation_body)
                elif self.cancel_ticket > i["numberOfTickets"]:
                    print(f"You booked only {i['numberOfTickets']}, You can't cancel more than that.")
        if not found_booking:
            print(f"{self.name} not found in the bookings.")

        self.bus_booking_menus()
    def send_email(self,to_email, subject, body):
        from_email = "dicro12347@gmail.com"
        password = "hwumijdjdewurliq"

        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(from_email, password)
            server.sendmail(from_email, to_email, msg.as_string())


Ticket()

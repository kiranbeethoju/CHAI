from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfbase import pdfform
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

class ImprovedFormGenerator:
    def __init__(self, output_path):
        self.output_path = output_path
        self.c = canvas.Canvas(output_path, pagesize=letter)
        self.width, self.height = letter
        
    def create_fillable_form(self):
        # Set title
        self.c.setFont("Helvetica-Bold", 14)
        self.c.drawString(self.width/2 - 80, self.height - 40, "Sample Fillable PDF Form")
        
        # Add description text
        self.c.setFont("Helvetica", 10)
        description = "Fillable PDF forms can be customised to your needs. They allow form recipients to fill out"
        description2 = "information on screen like a web page form, then print, save or email the results."
        self.c.drawString(50, self.height - 70, description)
        self.c.drawString(50, self.height - 85, description2)

        # Blue header for Fillable Fields
        self.c.setFillColor(colors.lightblue)
        self.c.rect(50, self.height - 120, self.width - 100, 20, fill=1)
        self.c.setFillColor(colors.black)
        self.c.setFont("Helvetica-Bold", 12)
        self.c.drawString(55, self.height - 115, "Fillable Fields")
        
        # Basic fields
        form = self.c.acroForm
        self.c.setFont("Helvetica", 10)
        
        # Name and Date fields
        self.c.drawString(50, self.height - 145, "Name")
        self.c.drawString(350, self.height - 145, "Date")
        
        form.textfield(
            name='name',
            tooltip='Enter Name',
            x=85,
            y=self.height - 160,
            width=250,
            height=20,
            borderColor=colors.black,
            fillColor=colors.white
        )
        
        form.textfield(
            name='date',
            tooltip='Enter Date',
            x=380,
            y=self.height - 160,
            width=150,
            height=20,
            borderColor=colors.black,
            fillColor=colors.white
        )
        
        # Address field
        self.c.drawString(50, self.height - 185, "Address")
        form.textfield(
            name='address',
            tooltip='Enter Address',
            x=85,
            y=self.height - 200,
            width=445,
            height=20,
            borderColor=colors.black,
            fillColor=colors.white
        )

        # Tick Boxes section
        self.c.setFillColor(colors.lightblue)
        self.c.rect(50, self.height - 260, self.width - 100, 20, fill=1)
        self.c.setFillColor(colors.black)
        self.c.setFont("Helvetica-Bold", 12)
        self.c.drawString(55, self.height - 255, "Tick Boxes (multiple options can be selected)")
        
        self.c.setFont("Helvetica", 10)
        self.c.drawString(50, self.height - 285, "What are your favourite activities?")
        
        # Checkboxes
        activities = ['Reading', 'Walking', 'Music', 'Other:']
        for i, activity in enumerate(activities):
            y_pos = self.height - 310 - (i * 25)
            form.checkbox(
                name=f'activity_{activity.lower().replace(":", "")}',
                tooltip=f'Select {activity}',
                x=50,
                y=y_pos,
                size=12,
                buttonStyle='check',
                borderColor=colors.black,
                fillColor=colors.white
            )
            self.c.drawString(70, y_pos + 3, activity)
            
            # Add text field for "Other"
            if activity == "Other:":
                form.textfield(
                    name='other_activity',
                    tooltip='Specify other activity',
                    x=120,
                    y=y_pos,
                    width=410,
                    height=15,
                    borderColor=colors.black,
                    fillColor=colors.HexColor('#F0F0F0')
                )

        # Radio Buttons section
        self.c.setFillColor(colors.lightblue)
        self.c.rect(50, self.height - 440, self.width - 100, 20, fill=1)
        self.c.setFillColor(colors.black)
        self.c.setFont("Helvetica-Bold", 12)
        self.c.drawString(55, self.height - 435, "Radio Buttons (only one option can be selected)")
        
        self.c.setFont("Helvetica", 10)
        self.c.drawString(50, self.height - 465, "What is your favourite activity?")
        
        # Radio buttons
        for i, activity in enumerate(activities):
            y_pos = self.height - 490 - (i * 25)
            form.radio(
                name='favorite_activity',
                tooltip=f'Select {activity}',
                value=activity.lower().replace(":", ""),
                x=50,
                y=y_pos,
                size=12,
                buttonStyle='circle',
                borderColor=colors.black,
                fillColor=colors.white
            )
            self.c.drawString(70, y_pos + 3, activity)
            
            # Add text field for "Other"
            if activity == "Other:":
                form.textfield(
                    name='other_favorite',
                    tooltip='Specify other favorite activity',
                    x=120,
                    y=y_pos,
                    width=410,
                    height=15,
                    borderColor=colors.black,
                    fillColor=colors.HexColor('#F0F0F0')
                )

        # Buttons section
        self.c.setFillColor(colors.lightblue)
        self.c.rect(50, self.height - 600, self.width - 100, 20, fill=1)
        self.c.setFillColor(colors.black)
        self.c.setFont("Helvetica-Bold", 12)
        self.c.drawString(55, self.height - 595, "Buttons (to prompt certain actions)")
        
        self.c.setFont("Helvetica", 10)
        self.c.drawString(50, self.height - 625, "These buttons can be printable or visible only when onscreen.")
        
        # Button placeholders with text
        self.c.setFont("Helvetica", 10)
        self.c.drawString(90, self.height - 680, "Print")
        self.c.drawString(190, self.height - 680, "Save")
        
        # Add "LOGO" text at the bottom
        self.c.setFont("Helvetica-Bold", 12)
        self.c.drawString(50, 50, "LOGO")
        
        # Add website
        self.c.setFont("Helvetica", 10)
        self.c.drawString(self.width - 200, 50, "www.worldofprinting.com")
        
        # Save the PDF
        self.c.save()

def generate_form(output_path='improved_fillable_form.pdf'):
    generator = ImprovedFormGenerator(output_path)
    generator.create_fillable_form()
    return output_path

if __name__ == "__main__":
    # Generate the form
    generate_form()
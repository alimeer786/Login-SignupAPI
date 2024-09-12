from django.db import models

class acessDB(models.Model):
    id = models.AutoField(primary_key=True)
    p_no = models.IntegerField()  # Part Number
    e_tag = models.CharField(max_length=255)  # Element Tag
    rev = models.IntegerField()  # Revision
    issue = models.DateField()  # Issue Date
    vol = models.DecimalField(max_digits=10, decimal_places=2)  # Volume
    qty = models.IntegerField()  # Quantity
    element = models.IntegerField()  # Element Identifier
    casting = models.DateField()  # Casting Date
    mix = models.CharField(max_length=255)  # Mix Description
    do = models.IntegerField()  # Delivery Order Number
    transporter = models.CharField(max_length=255)  # Transporter Name/ID
    qc = models.IntegerField()  # Quality Control Number/Status
    delivery = models.DateField()  # Delivery Date
    erection = models.DateField()  # Erection Date
    first_ir = models.IntegerField()  # First Inspection Report Number/Status
    ir_app = models.IntegerField()  # Inspection Report Approval Number/Status
    second_ir = models.IntegerField()  # Second Inspection Report Number/Status
    second_app = models.IntegerField()  # Second Approval Number/Status
    pa = models.IntegerField()  # Possible Approval Number/Status
    tr_no = models.IntegerField()  # Transport Receipt Number

    def __str__(self):
        return f"{self.e_tag} - {self.p_no}"

# # models.py
# from django.db import models

# class RegisteredAPI(models.Model):
#     name = models.CharField(max_length=255, unique=True)
#     endpoint_url = models.URLField()

#     def __str__(self):
#         return self.name

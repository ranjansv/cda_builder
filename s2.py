import pr

obj=pr.Patient()
obj.id="12345"
obj.given_name="Ranjan"
obj.last_name="Sarpangala"
obj.height="5.10"
obj.weight="120"
obj.bmi="20.2"
obj.village="bogadi"
obj.age="12 Y 9M"

obj.save_patient("./","alex_john_12345_05-29-2012-07-17-06_0")

obj=pr.Patient()
obj.id="435769"
obj.given_name="Robert"
obj.last_name="John"
obj.height="6.2"
obj.weight="140"
obj.bmi="23"
obj.village="patna"
obj.age="12 Y 4M"

obj.save_patient("./","bill_clinton_12345_05-29-2012-07-17-06_0")

obj=pr.Patient()
obj.id="935682"
obj.given_name="james"
obj.last_name="bill"
obj.height="5.8"
obj.weight="155"
obj.bmi="27.2"
obj.village="santa cruz"
obj.age="11 Y 3M"

obj.save_patient("./","smith_john_12345_05-29-2012-07-17-06_0")

obj=pr.Patient()
obj.id="882934"
obj.given_name="Alex"
obj.last_name="Steve"
obj.height="5.8"
obj.weight="90"
obj.bmi="24.3"
obj.village="hinkal"
obj.age="9 Y 6M"

obj.save_patient("./","thomas_john_12345_05-29-2012-07-17-06_0")


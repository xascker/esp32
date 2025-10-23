import wi_fi
import page


#page.run_code()
with open("page.py") as f:
    code1 = f.read()
exec(code1) 
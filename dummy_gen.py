import random
import string
from werkzeug.security import generate_password_hash
from lorem_text import lorem

L = string.ascii_letters
D = string.digits
LD = string.ascii_letters + string.digits


def get_random_alphaNumeric_string(stringLength=8):
    global L, D, LD
    return ''.join((random.choice(LD) for i in range(stringLength)))

def get_random_alpha_string(stringLength=8):
    global L, D, LD
    return ''.join((random.choice(L) for i in range(stringLength)))

def get_random_numeric_string(stringLength=8):
    global L, D, LD
    return ''.join((random.choice(D) for i in range(stringLength)))

def users_gen(size=10):
    global L, D, LD
    account_types = [('', ''), ('counselor', 'Counselor'),
                     ('student', 'Student'), ('tutor', 'Tutor')]
    majors = ['computer science', 'biology', 'psychology', 'physics', 'math', 'chemistry', 'business', \
              'electrical engineering', 'geology', 'anthropology']
    years = ['freshman', 'sophomore','junior','senior']

    ret = []
    for x in range(size):
        _id = get_random_numeric_string(11)
        username = get_random_alphaNumeric_string(5)
        email = get_random_alphaNumeric_string(5) + "@gmail.com"
        password = get_random_alphaNumeric_string(8 + (int)(random.choice(D)))
        # account_type = random.choice(account_types)
        major = random.choice(majors)
        account_type = 'student'
        year = random.choice(years)
        hashed_password = generate_password_hash(password, method='sha256')
        u = _id, username, email, hashed_password, account_type, major, year, password
        ret.append(u)
    return ret


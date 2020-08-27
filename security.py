from passlib.context import CryptContext
from dataAccess import addUser, usernameExists, emailExists, findPassword, initialiseSettings

# Password encryption taken from https://blog.tecladocode.com/learn-python-password-encryption-with-flask/
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    default="pbkdf2_sha256",
    pbkdf2_sha256__default_rounds=30000
)


def encrypt_password(password):
    return pwd_context.encrypt(password)


def check_encrypted_password(password, hashed):  # Checks a string against a stored hashed password returns boolean
    return pwd_context.verify(password, hashed)


def registerUser(form):
    # Assign a new id
    fName = form.fName.data.lower()
    sName = form.sName.data.lower()
    num = 1
    done = False
    while not done:
        assignedID = (fName[0] + "." + sName + str(num))  # Adds 1 to the end of the id
        if usernameExists(assignedID):
            num += 1
        else:
            done = True
    print(assignedID)

    school = form.school.data
    email = form.email.data
    password = form.password.data
    hashedPassword = encrypt_password(password)
    addUser(assignedID, fName, sName, school, email, hashedPassword)
    initialiseSettings(assignedID)


def validateLogin(form):
    usernameError = False
    passwordError = False
    if not usernameExists(form.username.data) and not emailExists(form.username.data):
        usernameError = True
    else:
        password = form.password.data
        hashedPassword = findPassword(form.username.data)
        if check_encrypted_password(password, hashedPassword):
            initialiseSettings(form.username.data)
        else:
            passwordError = True
    return usernameError, passwordError

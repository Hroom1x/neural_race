import pickle
default = {
    'fullscreen': [False, [True, False]]
    }
with open('default.pkl', 'wb') as file:
    pickle.dump(default, file)
choice = input('open default.pkl? "yes">> ')
if choice == 'yes':
    with open('default.pkl', 'rb') as file:
        printer = pickle.load(file)
    print(printer, '\n', type(printer))

import time
from helpers.image_exec import bresenhams_line, old_bresenhams_line

start = time.time()
tab1 = old_bresenhams_line((0,73), (99999,99999), 100000, 100000)
end = time.time()
print(f'old: {end-start}')

start = time.time()
tab2 = bresenhams_line((0,73), (99999,99999), 100000, 100000)
end = time.time()
print(f'new: {end-start}')


if tab1 == tab2: print('LETS GOOO')
else: print('Noo ;-;')
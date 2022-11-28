from re import sub

def snake_case(s):
  str1 = '_'.join(
    sub('([A-Z][a-z]+)', r' \1',
    sub('([A-Z]+)', r' \1',
    s.replace('-', ' '))).split()).lower().replace("&", "and")
  return sub("-[^a-zA-Z\d\s-]", "", str1)
  
def dash_case(s):
  str1 = '-'.join(
    sub('([A-Z][a-z]+)', r' \1',
    sub('([A-Z]+)', r' \1',
    s.replace('-', ' '))).split()).lower()
  return sub("-[^a-zA-Z\d\s-]", "", str1)
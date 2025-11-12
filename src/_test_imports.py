import sys
sys.path.insert(0, '.')
print('PYTHON PATH OK')
try:
    import src.chat
    print('IMPORTS_OK')
except Exception as e:
    print('IMPORT_ERROR', e)
    raise

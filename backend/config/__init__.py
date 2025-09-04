"""config package for backend refactor"""

# Setup PyMySQL as MySQLdb replacement for production
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass

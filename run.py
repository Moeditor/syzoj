from syzoj import oj
import sys
reload(sys)  # Reload does the trick!
sys.setdefaultencoding('UTF8')

if __name__ == '__main__':
    oj.debug = True
    oj.run(host="0.0.0.0", port=8811, threaded=True)

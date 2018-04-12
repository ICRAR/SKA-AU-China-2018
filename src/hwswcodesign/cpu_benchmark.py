from benchmarker import Benchmarker
import sys

loop = 1000
width = 20


def run(loop=1000, width=20):
    """
    Main run method
    """
    with Benchmarker(loop*loop, width=width) as bench:
        s1, s2, s3, s4, s5 = "Haruhi", "Mikuru", "Yuki", "Itsuki", "Kyon"

        @bench(None)                # empty loop
        def _(bm):
            for i in bm:
                pass

        @bench("join")
        def _(bm):
            for i in bm:
                sos = ''.join((s1, s2, s3, s4, s5))

        @bench("concat")
        def _(bm):
            for i in bm:
                sos = s1 + s2 + s3 + s4 + s5

        @bench("format")
        def _(bm):
            for i in bm:
                sos = '%s%s%s%s%s' % (s1, s2, s3, s4, s5)


def usage():
    """
    This code contains methods to perform performance tests of
    block devices, e.g. hard disks. It also allows using files rather
    than devices directly.

    Synopsis: cpu_benchmark.py [-l loop] [-w width] [-h]

          long arguments are allowed as well, e.g. --loop

          [l]oop:      integer, size of the loop. This will be used to size
                       the problem as a matrix, i.e. as l x l
          [w]idth:     integer
          [h]elp:      flag, if set this help text is shown.


    Author:  A. Wicenec [ICRAR]
    Date:    2018-04-12
    Version 0.1
    """
    import pydoc
    print pydoc.help('cpu_benchmark.usage')
    sys.exit()


if __name__ == '__main__':
    import getopt
    try:
        opts, args = getopt.getopt(
            sys.argv[1:], "l:w:h", ["loop=", "width=", "help"])
    except getopt.GetoptError as err:
        # print help information and exit:
        print str(err)  # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    for o, v in opts:
        if o in ("-l", "--loop"):
            loop = long(v)
        elif o in ("-w", "--width"):
            width = long(v)
        elif o in ("-h", "--help"):
            usage()
    run(loop=loop, width=width)

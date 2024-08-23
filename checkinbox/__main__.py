import getopt
import os
import sys
from typing import TextIO
import checkinbox

def printHelp (s: TextIO):
	s.write('''Usage: checkinbox [-h] [-V] [-F MAILFROM] [--] EMAIL_ADDRESS_SPEC
Options:
  -h             print help and exit normally
  -V             print version and exit normally
  -F <MAILFROM>  set the address for MAIL FROM: command.
                 Default: checkinbox@HOSTNAME

EMAIL_ADDRESS_SPEC:
  Accepts "To:" header value (comma separated list of email addresses). Format:
  [NAME] <EMAIL> | EMAIL[, EMAIL_ADDRESS_SPEC]

Exit codes:
  0: all inboxes exist
  1: fatal error
  2: usage error
  3: some inboxes exist
  4: no inboxes exist
''')

def printVer (s: TextIO):
	s.write(checkinbox.Version + os.linesep)

def doOptions () -> tuple[checkinbox.Options, list[str]]:
	ec = None
	opts = getopt.getopt(sys.argv[1:], 'hVF')
	ret_opts = checkinbox.Options()

	for k, v in opts[0]:
		if k == '-h':
			printHelp(sys.stdout)
			ec = 0
		elif k == '-V':
			printVer(sys.stdout)
			ec = 0
		elif k == '-F':
			ret_opts.mailfrom = v

	if ec is not None:
		exit(ec)

	return (ret_opts, opts[1])


try:
	opts, addr_spec = doOptions()
except getopt.GetoptError as e:
	sys.stderr.write(str(e) + os.linesep)
	exit(2)
addr_extracted = checkinbox.extractAddresses(' '.join(addr_spec))
if len(addr_extracted) == 0:
	sys.stderr.write('''No addresses. Use -h option for help.''' + os.linesep)
	exit(2)

results, errors = checkinbox.checkInboxes(addr_extracted, opts)
assert len(results) + len(errors) == len(addr_extracted)

x_cnt = 0
for a in addr_extracted:
	r = results.get(a)
	err = errors.get(a)

	if err:
		print('{0}: {1}'.format(a, err))
	elif r[0] != 250:
		print('{0}: {1} {2}'.format(a, r[0], str(r[1])))
		x_cnt += 1

if x_cnt == 0:
	exit(4)
if x_cnt != len(addr_extracted):
	exit(3)
exit(0)

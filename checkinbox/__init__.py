import re
import socket
import dns.exception
import dns.resolver
import smtplib
from typing import Any, Iterable

Version = "0.0.0"

class RE:
	BRACKETS = re.compile(r'''([^,<>\s]+@[^,<>\s]+)+''')

class Options:
	'''checkInboxes function options (reserved for future use)'''

	def __init__(self) -> None:
		self.mailfrom = 'checkinbox@' + socket.gethostname()

def extractAddresses (s: str) -> Iterable[str]:
	'''
	Extract addresses from the string in various formats as seen in the header,
	SMTP RCPT TO:, email client textbox separated with commas
		- <inbox@example.com>,
		- Account Payable <accounts@example.com>,
		- inbox@example.com,
	'''
	return RE.BRACKETS.findall(s)

def extractDomainPart (s: str) -> str:
	d = s.find('@')
	if d >= 0:
		return s[d + 1:]
	return ""

def mapMXRR (a: dns.resolver.Answer) -> dict[int, str]:
	ret = dict[int, str]()

	for rr in a:
		ret[rr.preference] = rr.exchange.to_text()

	return ret

def _connectAndCheck (a: str, mx: dict[int, str], opts: Options) -> tuple:
	last_err = None

	for pref, host in mx.items():
		try:
			with smtplib.SMTP(host) as c:
				c.starttls()

				rsp = c.docmd('MAIL FROM:<{0}>'.format(opts.mailfrom))
				if rsp[0] != 250:
					last_err = PermissionError(
						'MAIL FROM command failed',
						opts.mailfrom,
						rsp)
					break

				return c.docmd('RCPT TO:<{0}>'.format(a))
		except smtplib.SMTPException as e:
			last_err = e

	raise last_err

def checkInboxes (
		addresses: Iterable[str],
		opts: Options = None) -> tuple[dict[str, tuple], dict[str, Exception]]:
	result = dict[str, tuple]()
	err = dict[str, Exception]()
	opts = opts or Options()

	for a in addresses:
		domain = extractDomainPart(a)
		if len(domain) == 0:
			# may seem redundant - extractAddresses() returns addresses with domain parts only
			err[a] = ValueError('''{0}: no domain part'''.format(a))
			continue

		try:
			try:
				resolved = dns.resolver.resolve(domain, 'MX')
				mx = mapMXRR(resolved)
			except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
				mx = { 0: domain }

			result[a] = _connectAndCheck(a, mx, opts)
		except (
				dns.exception.DNSException,
				smtplib.SMTPException,
				PermissionError) as e:
			err[a] = e

	return (result, err)

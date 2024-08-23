# SMTP Inbox Checker
This is a simple CUI tool for testing the existence of email addresses. **The
TCP/25 port availability is required. Your ISP probably has that port blocked so
you wouldn't be able to use from your local machine. The command is meant to be
run on the server w/ all the DNS records configured for relaying.**

The command checks if the inbox exists simply by issuing `MAIL FROM` and `RCPT
TO` commands to the server. The command does not actually send any mail. The
command will refuse to work with servers without `STARTTLS` support.

## INSTALL
TODO: the package is not uploaded yet so ignore this section

```sh
pip install checkinbox
```

## Usage
```sh
python -m checkinbox inbox@example.com
```

See `python -m checkinbox -h` for more.

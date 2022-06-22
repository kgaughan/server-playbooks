require ["vnd.dovecot.pipe", "copy", "imapsieve", "environment"];

if environment :matches "imap.mailbox" ["Junk"] {
  pipe :copy "learn-spam";
}

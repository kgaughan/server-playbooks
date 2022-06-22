require ["vnd.dovecot.pipe", "copy", "editheader", "imapsieve", "environment"];

if environment :matches "imap.mailbox" ["Trash"] {
  stop;
}

deleteheader "X-Spam";
pipe :copy "learn-ham";

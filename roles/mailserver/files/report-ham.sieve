require ["vnd.dovecot.pipe", "copy", "editheader", "imapsieve", "environment"];

if not environment :matches "imap.mailbox" ["Trash"] {
  deleteheader "X-Spam";
  pipe :copy "learn-ham";
}

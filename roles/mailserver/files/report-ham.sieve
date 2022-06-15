require ["vnd.dovecot.pipe", "copy", "editheader", "imapsieve", "environment", "variables"];

if environment :matches "imap.mailbox" "*" {
  set "mailbox" "${1}";
}

if string "${mailbox}" ["Trash"] {
  stop;
}

if environment :matches "imap.user" "*" {
  set "username" "${1}";
}

deleteheader "X-Spam";
pipe :copy "learn-ham" ["${username}"];

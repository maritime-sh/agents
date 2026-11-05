# Security

Please report security issues privately by email to **contact@maritime.sh**, not in a public issue. We reply within two business days.

Scope: the scripts in this repository and the way they handle keys and computers. Issues in an upstream agent belong to that project; we are happy to help route them.

How keys are handled here:

- Keys are read from environment variables at run time and are never written into this repository.
- When an agent needs a model key inside its computer, the deploy script writes it to a file under `/data` that only the computer's user can read, on your own computer only.
- Every computer is its own micro-VM. Delete it from the Maritime dashboard when you are done to remove its disk.

# subdivxfind

Find a subtitle by release tag on subdivx.com.

Say you got your hands on the KILLERS release of movie Spam, you can run subdivxfind to search in the description and the comments of each subtitle at subdivx.com running:

```
subdivxfind Spam KILLERS
```

## Note

subdivx.com returns different content depending on whether the request is made by a logged in user or not. If the request is not made by a logged in user (the way subdivxfind behaves), the following changes occur to the subtitle description text:

* Text is lowercased
* Periods are replaced with spaces
* The strings "bluray", "dvd", "dvdrip", "xvid" (among others, presumably) are deleted
Feedback XBlock
==========

This is a basic clone of Dropthought for use in Open edX. This used to
be called the RateXBlock. We renamed it for better consistency. We are
keeping the old one around for backwards-compatibility.

The goal of this XBlock is two-fold:

1. Allow students to reflect on their learning experience
2. Provide instructors with feedback on which parts of courses work
   well and which parts work poorly.

Instructors have a good amount of control over the contents of
the block:

![Screenshot of the FeedbackXBlock -- good to bad scale](happy_sad_example.png)
![Screenshot of the FeedbackXBlock -- scale where good is in the middle](happy_sad_happy_example.png)
![Screenshot of the FeedbackXBlock -- numerical scale](numerical_example.png)

This can be placed anywhere in the courseware, and students can
provide feedback on those sections. With just a few database queries,
we can compile that feedback into useful insights. ;) We do provide
aggregate statistics to instructors, but not yet the text of the
feedback.

It installs on any Open edX install same as any other xblock:

    pip install -e git+https://github.com/pmitros/FeedbackXBlock.git#egg=rate==0.0

From there, add "feedback" to your list of advanced modules, and you're
good to go.

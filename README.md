# Center Stage

This is an open-source version of self-framing webcam. Center Stage is a personal experiment that was used to define, improve, and then abstract a face detection model and workflow. While Center Stage was not the primary focus of a face detection library for me, there did not exist any simple software that aimed to solve this problem.

Video conferences and meetings are tedious and keeping the framing just right can be a lot of work while you're trying to focus. So, Center Stage will make sure that you always are the center of attention and never get lost as you move around.

This is extremely resource intensive, so everything is handled on the GPU side of things.

## TODO

- [ ] Figure out how to build a CUDA implementation that will work on all computers instead of just mine...
    - [ ] This will always only work with NVIDIA GPUs?
- [ ] Figure out how to get Python -> Executable File.
- [ ] Figure out how to run app minimized in tray since all it really is, is a source connection.
- [ ] Confirm that this would already work for things like OBS if one was to setup a `Window Capture` on this window.
- [ ] Figure out how to get this to show up as source so that one could use it as a camera in things like Zoom.
    - This should be as simple as it is to setup Snap Camera.
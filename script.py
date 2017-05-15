import mdl
from display import *
from matrix import *
from draw import *

"""======== first_pass( commands, symbols ) ==========

  Checks the commands array for any animation commands
  (frames, basename, vary)
  
  Should set num_frames and basename if the frames 
  or basename commands are present

  If vary is found, but frames is not, the entire
  program should exit.

  If frames is found, but basename is not, set name
  to some default value, and print out a message
  with the name being used.

  jdyrlandweaver
  ==================== """

basename = "image"

def first_pass( commands ):
    num_frames = 1
    
    includes_frames = False
    includes_basename = False
    includes_vary = False
    for cmd in commands:
        if cmd[0] == "frames":
            num_frames = cmd[1]
            includes_frames = True
        elif cmd[0] == "basename":
            basename = cmd[1]
            includes_basename = True
        elif cmd[0] == "vary":
            includes_vary = True

    if includes_vary and not includes_frames:
        print "vary used without setting frames"
        exit(0)
    if includes_frames and not includes_basename:
        print "basename not specified. Using default 'image'"

    return num_frames
    

"""======== second_pass( commands ) ==========

  In order to set the knobs for animation, we need to keep
  a seaprate value for each knob for each frame. We can do
  this by using an array of dictionaries. Each array index
  will correspond to a frame (eg. knobs[0] would be the first
  frame, knobs[2] would be the 3rd frame and so on).

  Each index should contain a dictionary of knob values, each
  key will be a knob name, and each value will be the knob's
  value for that frame.

  Go through the command array, and when you find vary, go 
  from knobs[0] to knobs[frames-1] and add (or modify) the
  dictionary corresponding to the given knob with the
  appropirate value. 
  ===================="""
def second_pass( commands, num_frames ):
    #pass
    knobs = []
    for i in range(num_frames):
        knobs.append({})
    for cmd in commands:
        if cmd[0] == "vary":
            name = cmd[1]
            frame_start = cmd[2] #inclusive
            frame_end = cmd[3] #inclusive
            value_start = cmd[4]
            value_end = cmd[5]
            incr = 1.0 * (value_end - value_start) / (frame_end - frame_start + 1)
            value = value_start
            for i in range(frame_start, frame_end + 1):
                knobs[i][name] = value
                value += incr
    return knobs

def run(filename):
    """
    This function runs an mdl script
    """
    color = [255, 255, 255]

    p = mdl.parseFile(filename)

    if p:
        (commands, symbols) = p
    else:
        print "Parsing failed."
        return

    frames = first_pass(commands)
    isAnim = frames > 1
    
    if isAnim:
        knobs = second_pass(commands, frames)

    for frame in range(frames):
#        print frame
        tmp = new_matrix()
        ident(tmp)
        stack = [ [x[:] for x in tmp] ]
        screen = new_screen()
        tmp = []
        step = 0.1
        for command in commands:
#            print command
            c = command[0]
            args = command[1:]

            if c == 'box':
                add_box(tmp,
                    args[0], args[1], args[2],
                    args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, color)
                tmp = []
            elif c == 'sphere':
                add_sphere(tmp,
                       args[0], args[1], args[2], args[3], step)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, color)
                tmp = []
            elif c == 'torus':
                add_torus(tmp,
                      args[0], args[1], args[2], args[3], args[4], step)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, color)
                tmp = []
            elif c == 'move':
                tmp = make_translate(args[0], args[1], args[2])
                if args[3] != None:
                    knob_name = args[3]
                    scalar_mult(tmp, knobs[frame][knob_name])
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'scale':
                tmp = make_scale(args[0], args[1], args[2])
                if args[3] != None:
                    knob_name = args[3]
                    scalar_mult(tmp, knobs[frame][knob_name])
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'rotate':
                theta = args[1] * (math.pi/180)
                if args[0] == 'x':
                    tmp = make_rotX(theta)
                elif args[0] == 'y':
                    tmp = make_rotY(theta)
                else:
                    tmp = make_rotZ(theta)
                if args[2] != None:
                    knob_name = args[2]
                    scalar_mult(tmp, knobs[frame][knob_name])
                matrix_mult( stack[-1], tmp )
                stack[-1] = [ x[:] for x in tmp]
                tmp = []
            elif c == 'push':
                stack.append([x[:] for x in stack[-1]] )
            elif c == 'pop':
                stack.pop()
            elif c == 'display':
                display(screen)
            elif c == 'save':
                save_extension(screen, args[0])
                
            if isAnim:
                save_extension(screen, "anim/%s0%s" % (basename, frame))    

import argparse
import sys

from PIL import Image
import numpy as np

cols = 10

def ceildiv(a, b):
    return -(a // -b)

def main(argv):
    # parse arguments
    parser = argparse.ArgumentParser(description='Autostereogram generator')
    parser.add_argument('mask', help='the greyscale mask file to convert into an autosterogram')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--preset', choices=['static', 'six-color', 'grey', 'black/white'], default='static',
                         help='the randomized pattern to use')
    group.add_argument('--pattern',
                         help='the pattern file to use')

    parser.add_argument('-s', '--shift', type=int, default=10)
    parser.add_argument('-o', '--output', default='output.png')

    options = parser.parse_args(argv)

    # load image
    img = Image.open(options.mask).convert('L')
    img = np.array(img)
    img_height, img_width = img.shape

    # create/load pattern
    if options.pattern is not None:
        # load pattern file
        pat = np.array(Image.open(options.pattern))
        pat_height,pat_width,_ = pat.shape

        # extend pattern downward to needed height
        a,b = img_height//pat_height, img_height%pat_height
        arrs = [pat]*a + [pat[:b]]
        pat = np.concatenate(arrs)
        pat_height = img_height
    else:
        pat_height,pat_width = img_height,img_width//cols

        # generate the pattern
        match options.preset:
            case 'static':
                pat = np.random.randint(0, 256, [pat_height,pat_width,3])
            case 'six-color':
                pat = np.random.choice([0,255], [pat_height,pat_width,3])
            case 'grey':
                pat = np.random.randint(0, 256, [pat_height,pat_width])
                pat = np.stack([pat]*3, axis=2)
            case 'black/white':
                pat = np.random.choice([0,255], [pat_height,pat_width])
                pat = np.stack([pat]*3, axis=2)

        pat = np.uint8(pat)

    # extend pattern to right
    img_int32 = np.int32(img)

    output = np.empty([img_height,img_width,3], dtype=np.uint8)
    output[:,:pat_width] = pat
    for x in range(img_width):
        shift = options.shift
        arr = 255-img_int32[:,x]
        shift = (shift*arr + 128) // 256
        #shifted = x - pat_width + shift
        #shifted = np.where(shifted < 0, shifted+pat_width, shifted)
        shifted = x + shift
        shifted = np.where(shifted < pat_width, shifted, shifted-pat_width)
        output[:,x] = output[range(pat_height), shifted]

    #print(np.array_equal(output[:,:img_width], _output))

    # save output
    #output = np.moveaxis(output, 3, 0)
    #data = [Image.fromarray(frame) for frame in output]
    #data[0].save('output.gif', save_all=True, append_images=data[1:], duration=50, loop=0)
    data = Image.fromarray(output)
    data.save(options.output)

if __name__ == '__main__':
    if not main(sys.argv[1:]):
        sys.exit(1)


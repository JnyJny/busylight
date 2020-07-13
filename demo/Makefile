


all: demo.gif

FFMPEG_FLAGS= -vf
FFMPEG_FLAGS += "fps=10,scale=320:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse"
FFMPEG_FLAGS += -loop 0

demo.gif: demo.mov
	ffmpeg -i $< $(FFMPEG_FLAGS) $@


#	convert -layers Optimize tmp.gif $@

clean:
	@/bin/rm -f demo.gif

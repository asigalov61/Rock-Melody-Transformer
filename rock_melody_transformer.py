# -*- coding: utf-8 -*-
"""Rock_Melody_Transformer.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/github/asigalov61/Rock-Melody-Transformer/blob/main/Rock_Melody_Transformer.ipynb

# Rock Melody Transformer (ver. 1.0)

***

Powered by tegridy-tools: https://github.com/asigalov61/tegridy-tools

***

WARNING: This complete implementation is a functioning model of the Artificial Intelligence. Please excercise great humility, care, and respect. https://www.nscai.gov/

***

#### Project Los Angeles

#### Tegridy Code 2024

***

# (GPU CHECK)
"""

#@title NVIDIA GPU check
!nvidia-smi

"""# (SETUP ENVIRONMENT)"""

#@title Install dependencies
!git clone --depth 1 https://github.com/asigalov61/Rock-Melody-Transformer
!pip install huggingface_hub
!pip install einops
!pip install torch-summary
!apt install fluidsynth #Pip does not work for some reason. Only apt works

# Commented out IPython magic to ensure Python compatibility.
#@title Import modules

print('=' * 70)
print('Loading core Rock Melody Transformer modules...')

import os
import copy
import pickle
import secrets
import statistics
from time import time
import tqdm

print('=' * 70)
print('Loading main Rock Melody Transformer modules...')
import torch

# %cd /content/Rock-Melody-Transformer

import TMIDIX

from midi_to_colab_audio import midi_to_colab_audio

from x_transformer_1_23_2 import *

import random

# %cd /content/
print('=' * 70)
print('Loading aux Rock Melody Transformer modules...')

import matplotlib.pyplot as plt

from torchsummary import summary
from sklearn import metrics

from IPython.display import Audio, display

from huggingface_hub import hf_hub_download

from google.colab import files

print('=' * 70)
print('Done!')
print('Enjoy! :)')
print('=' * 70)

"""# (LOAD MODEL)"""

#@title Load Rock Melody Transformer Pre-Trained Model

#@markdown Model precision option

model_precision = "bfloat16" # @param ["bfloat16", "float16"]

#@markdown bfloat16 == Half precision/faster speed (if supported, otherwise the model will default to float16)

#@markdown float16 == Full precision/fast speed

plot_tokens_embeddings = False # @param {type:"boolean"}

print('=' * 70)
print('Loading Rock Melody Transformer Pre-Trained Model...')
print('Please wait...')
print('=' * 70)

full_path_to_models_dir = "/content/Rock-Melody-Transformer/Model"

model_checkpoint_file_name = 'Rock_Melody_Transformer_Medium_Trained_Model_21749_steps_0.7973_loss_0.7597_acc.pth'
model_path = full_path_to_models_dir+'/'+model_checkpoint_file_name
if os.path.isfile(model_path):
  print('Model already exists...')

else:
  hf_hub_download(repo_id='asigalov61/Rock-Melody-Transformer',
                  filename=model_checkpoint_file_name,
                  local_dir='/content/Rock-Melody-Transformer/Model',
                  local_dir_use_symlinks=False)

print('=' * 70)
print('Instantiating model...')

device_type = 'cuda'

if model_precision == 'bfloat16' and torch.cuda.is_bf16_supported():
  dtype = 'bfloat16'
else:
  dtype = 'float16'

if model_precision == 'float16':
  dtype = 'float16'

ptdtype = {'bfloat16': torch.bfloat16, 'float16': torch.float16}[dtype]
ctx = torch.amp.autocast(device_type=device_type, dtype=ptdtype)

SEQ_LEN = 4096 # Models seq len
PAD_IDX = 2081 # Models pad index

# instantiate the model

model = TransformerWrapper(
    num_tokens = PAD_IDX+1,
    max_seq_len = SEQ_LEN,
    attn_layers = Decoder(dim = 1024, depth = 24, heads = 16, attn_flash = True)
    )

model = AutoregressiveWrapper(model, ignore_index = PAD_IDX, pad_value=PAD_IDX)

model.cuda()
print('=' * 70)

print('Loading model checkpoint...')

model.load_state_dict(torch.load(model_path))
print('=' * 70)

model.eval()

print('Done!')
print('=' * 70)

print('Model will use', dtype, 'precision...')
print('=' * 70)

# Model stats
print('Model summary...')
summary(model)

# Plot Token Embeddings
if plot_tokens_embeddings:
  tok_emb = model.net.token_emb.emb.weight.detach().cpu().tolist()

  cos_sim = metrics.pairwise_distances(
    tok_emb, metric='cosine'
  )
  plt.figure(figsize=(7, 7))
  plt.imshow(cos_sim, cmap="inferno", interpolation="nearest")
  im_ratio = cos_sim.shape[0] / cos_sim.shape[1]
  plt.colorbar(fraction=0.046 * im_ratio, pad=0.04)
  plt.xlabel("Position")
  plt.ylabel("Position")
  plt.tight_layout()
  plt.plot()
  plt.savefig("/content/Rock-Melody-Transformer-Tokens-Embeddings-Plot.png", bbox_inches="tight")

"""# (GENERATE)

# (SETUP MODEL CHANNELS MIDI PATCHES)
"""

# @title Setup and load model channels MIDI patches

model_channel_0_piano_family = "Acoustic Grand" # @param ["Acoustic Grand", "Bright Acoustic", "Electric Grand", "Honky-Tonk", "Electric Piano 1", "Electric Piano 2", "Harpsichord", "Clav"]
model_channel_1_chromatic_percussion_family = "Music Box" # @param ["Celesta", "Glockenspiel", "Music Box", "Vibraphone", "Marimba", "Xylophone", "Tubular Bells", "Dulcimer"]
model_channel_2_organ_family = "Church Organ" # @param ["Drawbar Organ", "Percussive Organ", "Rock Organ", "Church Organ", "Reed Organ", "Accordion", "Harmonica", "Tango Accordion"]
model_channel_3_guitar_family = "Acoustic Guitar(nylon)" # @param ["Acoustic Guitar(nylon)", "Acoustic Guitar(steel)", "Electric Guitar(jazz)", "Electric Guitar(clean)", "Electric Guitar(muted)", "Overdriven Guitar", "Distortion Guitar", "Guitar Harmonics"]
model_channel_4_bass_family = "Fretless Bass" # @param ["Acoustic Bass", "Electric Bass(finger)", "Electric Bass(pick)", "Fretless Bass", "Slap Bass 1", "Slap Bass 2", "Synth Bass 1", "Synth Bass 2"]
model_channel_5_strings_family = "Violin" # @param ["Violin", "Viola", "Cello", "Contrabass", "Tremolo Strings", "Pizzicato Strings", "Orchestral Harp", "Timpani"]
model_channel_6_ensemble_family = "Choir Aahs" # @param ["String Ensemble 1", "String Ensemble 2", "SynthStrings 1", "SynthStrings 2", "Choir Aahs", "Voice Oohs", "Synth Voice", "Orchestra Hit"]
model_channel_7_brass_family = "Trumpet" # @param ["Trumpet", "Trombone", "Tuba", "Muted Trumpet", "French Horn", "Brass Section", "SynthBrass 1", "SynthBrass 2"]
model_channel_8_reed_family = "Alto Sax" # @param ["Soprano Sax", "Alto Sax", "Tenor Sax", "Baritone Sax", "Oboe", "English Horn", "Bassoon", "Clarinet"]
model_channel_9_pipe_family = "Flute" # @param ["Piccolo", "Flute", "Recorder", "Pan Flute", "Blown Bottle", "Skakuhachi", "Whistle", "Ocarina"]
model_channel_10_drums_family = "Drums" # @param ["Drums"]

print('=' * 70)
print('Setting up patches...')
print('=' * 70)

instruments = [v[1] for v in TMIDIX.Number2patch.items()]

patches = [instruments.index(model_channel_0_piano_family),
                       instruments.index(model_channel_1_chromatic_percussion_family),
                       instruments.index(model_channel_2_organ_family),
                       instruments.index(model_channel_3_guitar_family),
                       instruments.index(model_channel_4_bass_family),
                       instruments.index(model_channel_5_strings_family),
                       instruments.index(model_channel_6_ensemble_family),
                       instruments.index(model_channel_7_brass_family),
                       instruments.index(model_channel_8_reed_family),
                       9, # Drums patch
                       instruments.index(model_channel_9_pipe_family),
                       ] + [0, 0, 0, 0, 0]

print('Done!')
print('=' * 70)

"""# (IMPROV)"""

#@title Standard Improv Generator

#@markdown Generation settings

number_of_tokens_to_generate = 512 # @param {type:"slider", min:40, max:8192, step:4}
number_of_batches_to_generate = 4 #@param {type:"slider", min:1, max:16, step:1}
temperature = 0.9 # @param {type:"slider", min:0.1, max:1, step:0.05}

#@markdown Other settings

render_MIDI_to_audio = True # @param {type:"boolean"}

print('=' * 70)
print('Rock Melody Transformer Standard Improv Model Generator')
print('=' * 70)

outy = [random.randint(12, 24)+2056] + [0]

print('Selected Improv sequence:')
print(outy)
print('=' * 70)

torch.cuda.empty_cache()

inp = [outy] * number_of_batches_to_generate

inp = torch.LongTensor(inp).cuda()

with ctx:
  out = model.generate(inp,
                        number_of_tokens_to_generate,
                        temperature=temperature,
                        return_prime=True,
                        verbose=True)

out0 = out.tolist()

print('=' * 70)
print('Done!')
print('=' * 70)

torch.cuda.empty_cache()

#======================================================================

print('Rendering results...')

for i in range(number_of_batches_to_generate):

  print('=' * 70)
  print('Batch #', i)
  print('=' * 70)

  out1 = out0[i]

  print('Sample INTs', out1[:12])
  print('=' * 70)

  if len(out1) != 0:

      song = out1
      song_f = []

      time = 0
      dur = 32
      channel = 0
      pitch = 60
      vel = 90

      for ss in song:

          if 0 <= ss < 256:

              time += ss * 16

          if 256 < ss < 512:

              dur =  (ss-256) * 16

          if 512 < ss < 2048:

              chan = (ss-512) // 128

              if chan == 11:
                channel = 9
              else:
                if chan > 8:
                  channel = chan + 1
                else:
                  channel = chan

              if channel == 9:
                patch = 128
              else:
                patch = channel * 8

              pitch = (ss-512) % 128

          if 2048 < ss < 2056:
              vel = ((ss - 2048)+1) * 15

              song_f.append(['note', time, dur, channel, pitch, vel, patch])

      data = TMIDIX.Tegridy_ms_SONG_to_MIDI_Converter(song_f,
                                                      output_signature = 'Rock Melody Transformer',
                                                      output_file_name = '/content/Rock-Melody-Transformer-Composition_'+str(i),
                                                      track_name='Project Los Angeles',
                                                      list_of_MIDI_patches=patches
                                                      )


      print('=' * 70)
      print('Displaying resulting composition...')
      print('=' * 70)

      fname = '/content/Rock-Melody-Transformer-Composition_'+str(i)

      if render_MIDI_to_audio:
        midi_audio = midi_to_colab_audio(fname + '.mid')
        display(Audio(midi_audio, rate=16000, normalize=False))

      TMIDIX.plot_ms_SONG(song_f, plot_title=fname)

"""# (ROCK MELODY COMPOSITION GENERATION)"""

#@title Load Seed MIDI

#@markdown Press play button to to upload your own seed MIDI or to load one of the provided sample seed MIDIs from the dropdown list below

select_seed_MIDI = "Upload your own custom MIDI" # @param ["Upload your own custom MIDI", "Rock-Melody-Transformer-Melody-Seed-1", "Rock-Melody-Transformer-Melody-Seed-2", "Rock-Melody-Transformer-Melody-Seed-3", "Rock-Melody-Transformer-Melody-Seed-4", "Rock-Melody-Transformer-Melody-Seed-5", "Rock-Melody-Transformer-Melody-Seed-6", "Rock-Melody-Transformer-Melody-Seed-7"]
render_MIDI_to_audio = False # @param {type:"boolean"}

print('=' * 70)
print('Rock Melody Transformer Seed MIDI Loader')
print('=' * 70)

f = ''

if select_seed_MIDI != "Upload your own custom MIDI":
  print('Loading seed MIDI...')
  f = '/content/Rock-Melody-Transformer/Seeds/'+select_seed_MIDI+'.mid'

else:
  print('Upload your own custom MIDI...')
  print('=' * 70)
  uploaded_MIDI = files.upload()
  if list(uploaded_MIDI.keys()):
    f = list(uploaded_MIDI.keys())[0]

if f != '':

  print('=' * 70)
  print('File:', f)
  print('=' * 70)

  #=======================================================
  # START PROCESSING

  #===============================================================================
  # Raw single-track ms score

  raw_score = TMIDIX.midi2single_track_ms_score(f)

  #===============================================================================
  # Enhanced score notes

  escore_notes = TMIDIX.advanced_score_processor(raw_score, return_enhanced_score_notes=True)[0]

  escore_notes = [e for e in escore_notes if e[6] < 80 or e[6] == 128]

  #===============================================================================
  # Augmented enhanced score notes

  escore_notes = TMIDIX.augment_enhanced_score_notes(escore_notes)

  #===============================================================================
  # Chordified score
  dcscore = TMIDIX.chordify_score([1000, escore_notes])

  #===============================================================================

  output_score = []
  comp_tokens = []

  pc = dcscore[0]
  pc.sort(key=lambda x: x[4])

  for i, c in enumerate(dcscore[:-1]):

    c.sort(key=lambda x: x[4], reverse=True)
    cchans = sorted(set([x[3] for x in c]))

    nc = dcscore[i+1]
    nc.sort(key=lambda x: x[4], reverse=True)
    ncchans = sorted(set([x[3] for x in nc]))

    dtime = max(0, min(255, (c[0][1] - pc[0][1])))

    if 9 in ncchans:
      ncdrums = 1
    else:
      ncdrums = 0

    if ncchans == [9]:
      nctone = 24
    else:
      nctone = (12 * ncdrums) + (nc[0][4] % 12)

    output_score.append(nctone+2056)

    output_score.append(dtime)

    toks = []

    toks.extend([nctone+2056, dtime])

    for i, e in enumerate(c):

        dur = max(1, min(255, e[2]))

        if e[3] != 9:
          chan = e[6] // 8
        else:
          chan = 11

        ptc = max(1, min(127, e[4]))

        cha_ptc = (128 * chan) + ptc

        velocity = max(8, min(127, e[5]))
        vel = round(velocity / 15)-1

        output_score.extend([dur+256, cha_ptc+512, vel+2048])

        if i == 0:
          toks.extend([dur+256, cha_ptc+512, vel+2048])

    comp_tokens.append(toks)

    pc = c

  comp_tokens.append(toks)

  #=======================================================

  song_f = escore_notes

  comp_patches = sorted(set([e[6] for e in song_f]))

  for s in song_f:

    s[1] *= 16
    s[2] *= 16

  detailed_stats = TMIDIX.Tegridy_ms_SONG_to_MIDI_Converter(song_f,
                                                            output_signature = 'Rock Melody Transformer',
                                                            output_file_name = '/content/Rock-Melody-Transformer-Seed-Composition',
                                                            track_name='Project Los Angeles',
                                                            list_of_MIDI_patches=patches
                                                            )
  #=======================================================

  print('=' * 70)
  print('Composition stats:')
  print('Composition has', len(dcscore), 'chords')
  print('Composition MIDI patches:', comp_patches)
  print('=' * 70)

  print('Displaying resulting composition...')
  print('=' * 70)

  fname = '/content/Rock-Melody-Transformer-Seed-Composition'

  if render_MIDI_to_audio:
    midi_audio = midi_to_colab_audio(fname + '.mid')
    display(Audio(midi_audio, rate=16000, normalize=False))

  TMIDIX.plot_ms_SONG(song_f, plot_title=fname)

else:
  print('=' * 70)

#@title Rock composition generation

#@markdown NOTE: You can stop the generation at any time to render partial results

#@markdown Generation settings

generate_improv_intro = False # @param {type:"boolean"}
conditioning_type = "Tones-Times-Durations" # @param ["Tones", "Tones-Times", "Tones-Times-Durations", "Tones-Times-Durations-Pitches"]
number_of_chords_to_generate = 128 # @param {type:"slider", min:4, max:8192, step:4}
max_number_of_notes_per_chord = 12 # @param {type:"slider", min:1, max:16, step:1}
number_of_memory_tokens = 4096 # @param {type:"slider", min:32, max:8188, step:16}
temperature = 0.9 # @param {type:"slider", min:0.1, max:1, step:0.05}

#@markdown Other settings
render_MIDI_to_audio = True # @param {type:"boolean"}

print('=' * 70)
print('Rock Melody Transformer Model Generator')
print('=' * 70)

#===============================================================================

def generate_intro(num_tokens=128,
                   temperature=0.9
                   ):

  outy = [random.randint(12, 24)+2056] + [0]

  inp = [outy] * 1

  inp = torch.LongTensor(inp).cuda()

  with ctx:
    out = model.generate(inp,
                          num_tokens,
                          temperature=temperature,
                          return_prime=True,
                          verbose=True)


  out1 = out.tolist()[0]

  tidx = [i for i in range(len(out1[::-1])) if out1[::-1][i] < 256][0]

  out2 = out1[:-tidx-2]

  return out2

#===============================================================================

def generate_chords(input_seq,
                    next_time=255,
                    max_notes_limit = 10,
                    num_memory_tokens = 4096,
                    temperature=0.9):

    x = torch.tensor([input_seq] * 1, dtype=torch.long, device='cuda')

    o = 0

    ncount = 0

    time = 0

    ntime = next_time

    while (o < 2056 or o == 2080) and ncount < max_notes_limit and time < ntime:
      with ctx:
        out = model.generate(x[-num_memory_tokens:],
                            1,
                            temperature=temperature,
                            return_prime=False,
                            verbose=False)

      o = out.tolist()[0][0]

      if 0 < o < 256:
        ncount = 0
        time += o

      if 512 < o < 2048:
        ncount += 1

      if (o < 2056 or o == 2080) and time < ntime:
        x = torch.cat((x, out), 1)

    return x.tolist()[0][len(input_seq):]

#===============================================================================

print('Generating...')
print('=' * 70)

output = []
first_note = True
pidx = 0
sidx = 0

out = []
tidxs = []
dtime = 0

#===============================================================================

if conditioning_type == 'Tones':
  cond_type = 4

elif conditioning_type == 'Tones-Times':
  cond_type = 3

elif conditioning_type == 'Tones-Times-Durations':
  cond_type = 2

elif conditioning_type == 'Tones-Times-Durations-Pitches':
  cond_type = 1

#===============================================================================

if generate_improv_intro:
  print('Generating intro...')
  print('=' * 70)
  output = generate_intro()
  print('=' * 70)
  print('Generating continaution...')
  first_note = False
  pidx = 1
  cond_type = 4
  sidx = 1
  print('=' * 70)

#===============================================================================

torch.cuda.empty_cache()

pbar = tqdm.tqdm(total=len(comp_tokens[sidx:number_of_chords_to_generate]))

while pidx < len(comp_tokens[sidx:number_of_chords_to_generate])-1:

  c = comp_tokens[sidx:number_of_chords_to_generate][pidx]
  nc = comp_tokens[sidx:number_of_chords_to_generate][pidx+1]

  if cond_type > 3:
    ntime = 255
  else:
    ntime = nc[1]

  pidx += 1
  pbar.update(1)

  try:

    if output:
      tidxs.append(len(output))

    dtime = 0

    if out:
      dtime = sum([o for o in out if o < 256])

    if (c[0]-2056) < 12:
      output.extend([c[0]+12, c[1]-dtime, c[2], c[3], c[4]])

    else:
      output.extend([c[0], c[1]-dtime, c[2], c[3], c[4]])

    if first_note:
      output = output[:-1]
      first_note = False
    else:
      output = output[:-cond_type]

    out = []

    tries = 0

    while not out and tries < max_number_of_notes_per_chord:

      out = generate_chords(output,
                            next_time=ntime,
                            temperature=temperature,
                            max_notes_limit=max_number_of_notes_per_chord,
                            num_memory_tokens=number_of_memory_tokens
                            )

      tries += 1

    if tries == max_number_of_notes_per_chord:
      tidxs = tidxs[:-1]
      output = output[:tidxs[-1]]

      pidx -= 1

      out = []

      pbar.refresh()
      pbar.reset()
      pbar.update(pidx)

    else:
      output.extend(out)

  except KeyboardInterrupt:
    print('Stopping generation...')
    break

  except Exception as e:
    print('Error:', e)
    break

pbar.close()

torch.cuda.empty_cache()

#===============================================================================

print('=' * 70)
print('Done!')
print('=' * 70)

#===============================================================================

print('Rendering results...')

print('=' * 70)
print('Sample INTs', output[:12])
print('=' * 70)

if len(output) != 0:

    song = output
    song_f = []

    time = 0
    dur = 32
    channel = 0
    pitch = 60
    vel = 90

    for ss in song:

        if 0 <= ss < 256:

            time += ss * 16

        if 256 < ss < 512:

            dur =  (ss-256) * 16

        if 512 < ss < 2048:

            chan = (ss-512) // 128

            if chan == 11:
              channel = 9
            else:
              if chan > 8:
                channel = chan + 1
              else:
                channel = chan

            if channel == 9:
              patch = 128
            else:
              patch = channel * 8

            pitch = (ss-512) % 128

        if 2048 < ss < 2056:
            vel = ((ss - 2048)+1) * 15

            song_f.append(['note', time, dur, channel, pitch, vel, patch])

detailed_stats = TMIDIX.Tegridy_ms_SONG_to_MIDI_Converter(song_f,
                                                          output_signature = 'Rock Melody Transformer',
                                                          output_file_name = '/content/Rock-Melody-Transformer-Composition',
                                                          track_name='Project Los Angeles',
                                                          list_of_MIDI_patches=patches
                                                          )

#=========================================================================

print('=' * 70)
print('Displaying resulting composition...')
print('=' * 70)

fname = '/content/Rock-Melody-Transformer-Composition'

if render_MIDI_to_audio:
  midi_audio = midi_to_colab_audio(fname + '.mid')
  display(Audio(midi_audio, rate=16000, normalize=False))

TMIDIX.plot_ms_SONG(song_f, plot_title=fname)

"""# Congrats! You did it! :)"""
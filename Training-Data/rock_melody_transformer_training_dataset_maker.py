# -*- coding: utf-8 -*-
"""Rock_Melody_Transformer_Training_Dataset_Maker.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1lBtYkU8bfb_8a3Qres-lq0bOrmQZ-Jye

# Rock Melody Transformer Training Dataset Maker (ver. 1.0)

***

Powered by tegridy-tools: https://github.com/asigalov61/tegridy-tools

***

#### Project Los Angeles

#### Tegridy Code 2024

***

# (SETUP ENVIRONMENT)
"""

#@title Install all dependencies (run only once per session)

!git clone --depth 1 https://github.com/asigalov61/tegridy-tools

#@title Import all needed modules

print('Loading core modules. Please wait...')

import os
import copy
import math
import statistics
import random

from joblib import Parallel, delayed, parallel_config

from collections import Counter

from tqdm import tqdm

from google.colab import files

print('Creating IO dirs...')

if not os.path.exists('/content/Dataset'):
  os.makedirs('/content/Dataset')

if not os.path.exists('/content/INTS'):
  os.makedirs('/content/INTS')

print('Loading TMIDIX module...')
os.chdir('/content/tegridy-tools/tegridy-tools')

import TMIDIX

print('Done!')

os.chdir('/content/')
print('Enjoy! :)')

"""# (DOWNLOAD MIDI DATASET)"""

# Commented out IPython magic to ensure Python compatibility.
# @title Download and untar LAKH clean_midi MIDI subset
# %cd /content/Dataset/
!wget http://hog.ee.columbia.edu/craffel/lmd/clean_midi.tar.gz
!tar -xvf clean_midi.tar.gz
!rm clean_midi.tar.gz
# %cd /content/

"""# (FILE LIST)"""

#@title Save file list
###########

print('=' * 70)
print('Loading MIDI files...')
print('This may take a while on a large dataset in particular.')

dataset_addr = "/content/Dataset"

filez = list()
for (dirpath, dirnames, filenames) in os.walk(dataset_addr):
    for file in filenames:
        if file.endswith(('.mid', '.midi', '.kar')):
            filez.append(os.path.join(dirpath, file))
print('=' * 70)

if filez == []:
    print('Could not find any MIDI files. Please check Dataset dir...')
    print('=' * 70)

else:
  print('Randomizing file list...')
  random.shuffle(filez)
  print('=' * 70)

  TMIDIX.Tegridy_Any_Pickle_File_Writer(filez, '/content/filez')
  print('=' * 70)

#@title Load file list

print('=' * 70)
filez = TMIDIX.Tegridy_Any_Pickle_File_Reader('/content/filez')
print('Done!')
print('=' * 70)

"""# (PROCESS)"""

# @title Load TMIDIX MIDI Processor

print('=' * 70)
print('Loading TMIDIX MIDI Processor...')

def TMIDIX_MIDI_Processor(midi_file):

    try:

        fn = os.path.basename(midi_file)

        #=======================================================
        # START PROCESSING

        #===============================================================================
        # Raw single-track ms score

        raw_score = TMIDIX.midi2single_track_ms_score(midi_file)

        #===============================================================================
        # Enhanced score notes

        escore_notes = TMIDIX.advanced_score_processor(raw_score, return_enhanced_score_notes=True)[0]

        escore_notes = [e for e in escore_notes if e[6] < 80 or e[6] == 128]

        # checking number of instruments in a composition
        instruments_list = list(set([y[3] for y in escore_notes]))

        if len(escore_notes) > 0 and (9 in instruments_list):

            #=======================================================
            # PRE-PROCESSING

            #===============================================================================
            # Augmented enhanced score notes

            escore_notes = TMIDIX.augment_enhanced_score_notes(escore_notes, timings_divider=32)

            #===============================================================================
            # Chordified score
            dcscore = TMIDIX.chordify_score([1000, escore_notes])

            #===============================================================================

            dt_score_notes_vel = []

            npe = dcscore[0]
            npe.sort(key=lambda x: x[4])

            pe = 0

            ntime = 0
            pabs_time = 0

            abs_time = 0

            drums = False

            for i, d in enumerate(dcscore[:-1]):
              d.sort(key=lambda x: x[4])
              dchans = sorted(set([x[3] for x in d]))

              nd = dcscore[i+1]
              chans = sorted(set([x[3] for x in nd]))

              time = nd[0][1] - npe[0][1]

              dtime = max(0, min(127, time))

              pabs_time = abs_time

              abs_time += dtime

              npe = nd

              ndtime = abs_time - ntime

              ndtime = max(0, min(127, ndtime))

              if 9 in dchans and len(dchans) > 1:
                    drums = True

              dnotes = []
              ndnotes = []

              if drums:

                  ndnotes = sorted([n for n in nd if n[3] != 9], key=lambda x: -x[4])
                  dnotes = sorted([n for n in d if n[3] != 9], key=lambda x: -x[4])

                  if ndnotes:
                      ht = max(1, min(127, ndnotes[0][4])) % 12
                  else:
                      ht = 12

                  token = (ndtime * 13) + ht

                  dt_score_notes_vel.extend([token])

              ntime = abs_time

              pe = pabs_time

              if 9 in dchans:

                  for e in d:

                    cha = e[3]

                    if cha == 9:

                      cdtime = pabs_time - pe

                      cdtime = max(0, min(127, int(cdtime)))

                      ptc = max(1, min(127, e[4]))

                      if cdtime != 0:
                        dt_score_notes_vel.extend([cdtime+1664, ptc+1792])
                      else:
                        dt_score_notes_vel.extend([ptc+1792])

                      pe = pabs_time

              if 9 not in dchans and drums:
                  dt_score_notes_vel.extend([0+1792])

              if dnotes:
                for e in dnotes:

                    dur = max(1, min(127, e[2]))

                    chan = e[6] // 8

                    ptc = max(1, min(127, e[4]))

                    cha_ptc = (128 * chan) + ptc

                    dt_score_notes_vel.extend([dur+1920, cha_ptc+2048])

              if len(dt_score_notes_vel) > 8192:
                break

            #===============================================================================

            # TOTAL DICT SIZE 3328

            #===============================================================================

            dt_score_notes_vel = dt_score_notes_vel[:8193]

            if dt_score_notes_vel:
              return dt_score_notes_vel

            else:
              return None

        else:
          return None

    except Exception as e:
        print('=' * 70)
        print('ERROR!!!')
        print('File name:', midi_file)
        print('Error:', e)
        print('=' * 70)
        return None

print('Done!')
print('=' * 70)

#@title Process MIDIs with TMIDIX MIDI processor

NUMBER_OF_PARALLEL_JOBS = 16 # Number of parallel jobs
NUMBER_OF_FILES_PER_ITERATION = 16 # Number of files to queue for each parallel iteration
SAVE_EVERY_NUMBER_OF_ITERATIONS = 160 # Save every 2560 files

print('=' * 70)
print('TMIDIX MIDI Processor')
print('=' * 70)
print('Starting up...')
print('=' * 70)

###########

melody_chords_f = []

files_count = 0
good_files_count = 0

print('Processing MIDI files. Please wait...')
print('=' * 70)

for i in tqdm(range(0, len(filez), NUMBER_OF_FILES_PER_ITERATION)):

  with parallel_config(backend='threading', n_jobs=NUMBER_OF_PARALLEL_JOBS, verbose = 0):
    output = Parallel(n_jobs=NUMBER_OF_PARALLEL_JOBS, verbose=0)(delayed(TMIDIX_MIDI_Processor)(f) for f in filez[i:i+NUMBER_OF_FILES_PER_ITERATION])

  for o in output:

      if o is not None:
          melody_chords_f.append(o)

  # Saving every 2560 processed files
  if i % (SAVE_EVERY_NUMBER_OF_ITERATIONS * NUMBER_OF_FILES_PER_ITERATION) == 0 and i != 0:
      print('SAVING !!!')
      print('=' * 70)
      good_files_count += len(melody_chords_f)
      print('Saving processed files...')
      print('=' * 70)
      print('Data check:', min(melody_chords_f[0]), '===', max(melody_chords_f[0]), '===', len(list(set(melody_chords_f[0]))), '===', len(melody_chords_f[0]))
      print('=' * 70)
      print('Processed so far:', good_files_count, 'out of', i, '===', good_files_count / i, 'good files ratio')
      print('=' * 70)
      count = str(i)
      TMIDIX.Tegridy_Any_Pickle_File_Writer(melody_chords_f, '/content/INTS/UDT_INTs_'+count)
      melody_chords_f = []
      print('=' * 70)

print('SAVING !!!')
print('=' * 70)
good_files_count += len(melody_chords_f)
print('Saving processed files...')
print('=' * 70)
print('Data check:', min(melody_chords_f[0]), '===', max(melody_chords_f[0]), '===', len(list(set(melody_chords_f[0]))), '===', len(melody_chords_f[0]))
print('=' * 70)
print('Processed so far:', good_files_count, 'out of', i, '===', good_files_count / i, 'good files ratio')
print('=' * 70)
count = str(i)
TMIDIX.Tegridy_Any_Pickle_File_Writer(melody_chords_f, '/content/INTS/UDT_INTs_'+count)
print('=' * 70)

"""# (TEST INTS)"""

#@title Test training INTs

train_data1 = random.choice(melody_chords_f)

print('=' * 70)
print('Seq len:', len(train_data1))
print('Sample INTs', train_data1[:15])
print('=' * 70)

out = train_data1

if len(out) != 0:

    song = out
    song_f = []

    time = 0
    dtime = 0
    ntime = 0
    dur = 32
    vel = 90
    dpitch = 0
    channel = 0

    patches = [0, 10, 19, 24, 35, 40, 52, 56, 65, 9, 73, 46, 0, 0, 0, 0]
    patches[3] = 40

    for ss in song:

        if 0 < ss < 1664:

            dtime = ptime = time

            tim = ss // 13
            ton = ss % 13

            time += tim * 32

            if ton < 12:
                song_f.append(['note', time, dur, 11, 72+ton, 115, 46])

        if 1664 < ss < 1792:

            dtime += (ss-1664) * 32

        if 1792 <= ss < 1920:

            dpitch = (ss-1792)

            if dpitch != 0:
                song_f.append(['note', dtime, dur, 9, dpitch, 100, 128])

        if 1920 < ss < 2048:
            ndur = (ss - 1920) * 32

        if 2048 < ss < 3328:
            channel = (ss-2048) // 128

            if channel > 8:
              channel += 1

            nptc = (ss-2048) % 128

            song_f.append(['note', ptime, ndur, channel, nptc, 70, channel*8])

detailed_stats = TMIDIX.Tegridy_ms_SONG_to_MIDI_Converter(song_f,
                                                        output_signature = 'Rock Melody Transformer',
                                                        output_file_name = '/content/Rock-Melody-Transformer-Composition',
                                                        track_name='Project Los Angeles',
                                                        list_of_MIDI_patches=patches
                                                        )
print('=' * 70)

"""# (ZIP AND DOWNLOAD INTS)"""

# Commented out IPython magic to ensure Python compatibility.
#@title Zip and download training INTs

print('=' * 70)

try:
    os.remove('Ultimate_Drums_Transformer_INTs.zip')
except OSError:
    pass

print('Zipping... Please wait...')
print('=' * 70)

# %cd /content/INTS/
!zip Ultimate_Drums_Transformer_INTs.zip *.pickle
# %cd /content/

print('=' * 70)
print('Done!')
print('=' * 70)

print('Downloading final zip file...')
print('=' * 70)

files.download('/content/INTS/Ultimate_Drums_Transformer_INTs.zip')

print('Done!')
print('=' * 70)

"""# Congrats! You did it! :)"""
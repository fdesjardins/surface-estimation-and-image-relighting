# Surface Estimation and Relighting

<img src="https://github.com/user-attachments/assets/6f46adb0-b86d-4310-8afe-23e7046cf2f1" width="100%" />

## Overview

Decomposing an image into its constituent parts is a complex problem. A scene model, such as a typical computer graphics model, contains all the objects and effects in a world in a compact representation. Objects in a scene are typically surfaces, but may be lights, cameras, or even volumetric regions. These surfaces serve the basis for our lighting model.

Once the shape of the geometry in a scene is defined, it can be refined, made more physically accurate, by attaching information to it in the form of material parameters, textures, reflectance maps, normal maps, etc. Each of these parameters must then be estimated from a photograph to have the complete representation.

Even if all such parameters could be calculated, these are a small subset of local parameters that influence the final appearance of a rendered scene. Global parameters would need to be estimated as well. These are variables such as the color or intensity of the light source(s), global ambient light levels, camera parameters, or even Rayleigh Scattering due to atmospheric conditions where the photograph was taken.

### Surface Reconstruction

Previous approaches to estimating the shape of objects in an image try to use the shading cues at the point of inference. Some other approaches have attempted to use the shadows as hints about geometry shape as well. With advances in computer vision and machine learning, researchers have been able to reconstruct rudimentary surfaces using learning-based approaches.

Notably, Varol et al. use Gaussian Processes to try to reconstruct deformable lambertian surfaces. They accomplish this by predicting the shape of underlying geometry of patches of the original image. These patches are then aligned and linked together to form a complete surface. Like some other approaches, results are dependent on a complex calibration of the environment where the images are taken. This excludes the possibility of a generalized solution.

### Training Data

Synthetic training data is generated rather than using real world data. One, because we can ensure a variety of surface configurations, but also because it yields more consistent data across hundreds or thousands of samples. Using a physically-based rendering system, we can create a data generation solution that is consistent over millions of samples.

First, mesh templates are defined. These templates are a series of subdivisions of a simple quad primitive defined by four corner points. Next, a jittering operation is applied to each mesh.

This perturbation of vertices is the basis for the discriminability of the classifiers. This operation yields every combination of the template vertices at the given depths. The user can explore the jittered data under different lighting conditions, etc., via the user interface. Ultimately, each jittered mesh is exported to the ray tracer LuxRender.

### Training the Classifiers

Support Vector Machines are used as the classifiers and are trained using an RBF kernel. Each rendered image patch is a 64-pixel (8x8) intensity image that maps to a 2x2 mesh patch. A grid search is performed during testing over the C and Gamma parameters. Lights are rendered at many different locations in the new images that serve as samples of each mesh configuration.


### Predicting Patches

Images are processed using a sliding-window approach, where each patch defined by a given patch size, 8x8 in our case, is run through every classifier trained previously. There are 512 classifiers, so images can take quite a while to be processed. Multiprocessing is used to speed up the process. Also, because 8x8 intensity patches map to 2x2 meshes, we need to process the input image at a relatively high resolution, or the resolution of the produced mesh will also be too low to be useful.


### Global Alignment

Global alignment is the final step before the reconstructed mesh can be displayed. This is a two-step process: The first step refines the predictions of the classifiers by making them consistent with spatially local predictions, the second step attempts to make the mesh consistent by shifting the next patch to be added to the mesh in the z direction. That is, it shifts the patch so that the vertices on the edges line up with previous meshes as much as possible.

Last, smoothing is applied to the mesh vertices in the same way images are smoothed used a Gaussian filter, using z values instead of intensity values. Smoothing needs to be applied at several points during this algorithm, and the best results come from manually adjusting the amount of smoothing at each step in the process.

### Relighting with LuxRender

After both surface reconstruction and radial gradient detection, it is possible to perform rudimentary image relighting operations with little additional information. Though the process has been automatic up to this point, the user must specify the material properties of the surfaces in the scene.

The entire input image is assumed to be simple; either there is a single object, or there are several objects with the same or similar material properties. The alternative is automatic segmentation of the input image into regions defined by texture, color, and spatial location, and this may be a useful extension to the system in the future.

## Setup

```bash
sudo apt-get install libamd2.2.0 libblas3gf libc6 libgcc1 libgfortran3 liblapack3gf libumfpack5.4.0 libstdc++6 build-essential gfortran python-all-dev libpng12-dev libfreetype6-dev cmake qt4-qmake libqt4-core libqt4-dev python-setuptools python-pip
pip install numpy scipy matplotlib scikit-learn
```

download and install luxrender

### Using homebrew

Note: you may need libjpeg, libtiff before installing pil

```bash
brew install pip
sudo pip install numpy scipy matplotlib scikits.learn PyOpenGL pil
```

Download and install LuxRender for OSX (http://www.luxrender.net/en_GB/download)

## Usage (and shortcuts)

### jittering
```
python main.py jitter 2 0
```

### reconstruct a surface
```
python scripts/predict.py /path/to/imagefile
python main.py recon /path/to/imagefile
```

### after reconstruction

You can create an image or video reconstruction yields a .lxs file, which can be edited and values such as light position changed

```
python scripts/makevid.py
```

### training the SVMs (uses data/2x2 image patches)
```
python scripts/train.py
```

### generating training data (careful, will overwrite existing)
```
cd scripts/
python gen_training_data.py
```

### viewing an image
```
python scripts/view/view_image.py /path/to/imagefile
```

### shortcuts

The OpenGL interface supports several commands depending on what you're doing:
(for example, normals are computed by default during the reconstruction)

```
KEY   ACTION
n     show normals
p     show ppixel lighting
w     show wireframe
t     show passthrough (plain surface, no shading)
v     show vertices
o     show orthographic projection
e     export mesh to luxrender
c     view continuous reconstruction of current mesh

left   previous jitter configuration
right  next jitter configuration
up	   next higher quad subdivision to use for jittering (careful! blows up fast)
down   next lower quad subdivision to use
```

```
MOUSE   ACTION
left    pan
right   rotate
middle  zoom
scroll  zoom
```

# License

MIT © Forrest Desjardins

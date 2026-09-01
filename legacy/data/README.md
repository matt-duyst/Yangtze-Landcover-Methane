# Source images for the 2023 notebook

These are the nine images that `Duyst_Thesis_Final.ipynb` reads by literal
filename. They were removed from the repository in commit `b0778b8`, "Delete
JPGs directory", and have been restored here from the object store, where they
had remained reachable the whole time. Each file was extracted with
`git cat-file` from the tree at `b0778b8^` and verified against its blob by
byte count and SHA-256, so the bytes here are the bytes the notebook ran on.

They are lossy JPEG renderings rather than georeferenced rasters. None carries
a coordinate reference system, a geotransform, or a nodata value, and the
compression has introduced spurious intermediate values along class boundaries
in what were originally clean masks. The urban and rice files are near-binary
masks whose foreground is close to zero and whose background sits at 240 and
255 respectively. `XCH4_2018.jpg` is not a concentration field at all; it is a
grayscale flattening of a colour-ramp choropleth, in which 81.5% of pixels hold
the single value 255 because that is the white page background of the figure
that was flattened. Grayscale conversion of a red-orange-yellow-green ramp is
not monotonic in the quantity being mapped, so distances in these pixel values
do not correspond to distances in parts per billion.

The rebuilt pipeline does not use any of these files. It reads source data in
its native form, and these are preserved only so that the original notebook's
inputs remain available to anyone who wants to run it as it was written or to
check a claim in the 2023 thesis against what the code actually consumed.
Section 3.1 of `ERRATA.md` sets out what the character of these files means for
the results reported from them.

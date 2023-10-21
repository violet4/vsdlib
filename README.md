# vsdlib
A python framework for easily creating a custom Stream Deck user interface

VSDLib makes it easier to customize button appearance (image, or text+background color), create structured layouts, multiple pages.

VSDLib is short for "violet stream deck library".

[violet_streamdeck](https://github.com/violet4/violet_streamdeck) is a program that demonstrates the use of vsdlib.

# Getting Started

```toml
# example.toml

# custom colors that can be referenced by name
[colors]
light_pink='#f77'

[c0.r0]
# the button will display the text "g"
text="g"
# when pressed, the button will type the character "g"
key="g"
# reference to `light_pink` from the `colors` section above
color='light_pink'
```

See more examples in [example.toml](example.toml).

Then you can run it with:

`poetry run vsdlib example.toml`

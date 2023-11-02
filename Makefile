all: main

main: src/main.c
    gcc -o bin/main src/main.c

install:
    install -Dm755 bin/main /usr/bin/my-package

clean:
    rm -f bin/main

.PHONY: package manifest build

build:
    mkdir -p build
    cd build && ../configure
    $(MAKE) -C build

package:
	tar -czvf ebuilds/my-package/files/my-package-1.0.tar.gz src Makefile.am configure.ac

manifest:
	cd ebuilds/my-package && ebuild my-package-1.0.ebuild manifest

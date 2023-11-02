# my-package-1.0.ebuild
EAPI=7

DESCRIPTION="A simple hello world program"
HOMEPAGE="https://example.com/my-package"
SRC_URI="https://example.com/my-package/files/${P}.tar.gz"

LICENSE="MIT"
SLOT="0"
KEYWORDS="~amd64 ~x86"
IUSE=""

DEPEND="acct-user/vsdlib acct-group/vsdlib"
RDEPEND="${DEPEND}"

src_configure() {
    ./configure || die "Configuration failed"
}

src_compile() {
    emake
}

src_install() {
    emake install
}

PREFIX = /usr/local

all:
	cd tools; ./generate_mo.py; cd ..

install:
	mkdir -p ${DESTDIR}${PREFIX}/bin
	mkdir -p ${DESTDIR}${PREFIX}/share/applications
	mkdir -p ${DESTDIR}${PREFIX}/share/deepin-game
	mkdir -p ${DESTDIR}${PREFIX}/share/icons/hicolor/scalable/apps
	cp -r src ${DESTDIR}${PREFIX}/share/deepin-game
	cp -r skin ${DESTDIR}${PREFIX}/share/deepin-game
	cp -r data ${DESTDIR}${PREFIX}/share/deepin-game
	cp -r locale/mo ${DESTDIR}${PREFIX}/share/locale
	cp -r app_theme ${DESTDIR}${PREFIX}/share/deepin-game
	cp -r image ${DESTDIR}${PREFIX}/share/deepin-game
	cp -r static ${DESTDIR}${PREFIX}/share/deepin-game
	cp -r weibo_skin ${DESTDIR}${PREFIX}/share/deepin-game
	cp -r weibo_theme ${DESTDIR}${PREFIX}/share/deepin-game
	cp image/deepin-game-center.svg ${DESTDIR}${PREFIX}/share/icons/hicolor/scalable/apps
	cp deepin-game-center.desktop ${DESTDIR}${PREFIX}/share/applications
	ln -sf ${PREFIX}/share/deepin-game/src/deepin-game-center.py ${DESTDIR}${PREFIX}/bin/deepin-game-center

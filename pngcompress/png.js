var totalFile = 0;
var originSize = 0;
var newSize = 0;
var fileList = [];

var fs = require('fs');
var path = require('path');
var execSync = require('child_process').execSync;

function walk(dir) {
	var dirList = fs.readdirSync(dir),
		temp;
	dirList.forEach(function(item) {
		temp = dir + '/' + item;
		var states = fs.statSync(temp);
		if (states.isDirectory()) {
			walk(temp);
		} else {
			var relPath = path.relative(process.cwd(), temp);
			var ext = path.extname(relPath);
			if (ext === '.png') {
				++totalFile;
				var oldSize = states.size;
				originSize = originSize + oldSize;
				execSync('pngquant.exe -f --speed 1 ' + relPath + ' --ext ' + '.png');
				execSync('optipng.exe -strip all -quiet -clobber -o3 -i0 ' + relPath);
				states = fs.statSync(temp);
				newSize = newSize + states.size;
				console.log(relPath, (oldSize / 1024).toFixed(2), (states.size / 1024).toFixed(2), 'K');
			}
		}
	});
}

walk(path.resolve(process.cwd()));
console.log('原png总大小：', (originSize / 1024).toFixed(2), 'K');
console.log('现png总大小：', (newSize / 1024).toFixed(2), 'K');
console.log('总节省大小：', ((originSize - newSize) / 1024).toFixed(2), 'K');
console.log('压缩比：', (((originSize - newSize) / originSize) * 100).toFixed(2), '%');

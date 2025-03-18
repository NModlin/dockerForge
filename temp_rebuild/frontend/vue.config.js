module.exports = {
  publicPath: '/static/',
  outputDir: process.env.NODE_ENV === 'production' ? 'dist' : 'dist',
  assetsDir: '',
  productionSourceMap: false
}

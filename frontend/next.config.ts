/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
    ];
  },
  images: {
    domains: [
      'media.api-sports.io',
      'media-4.api-sports.io',
      'media-3.api-sports.io',
      'media-2.api-sports.io',
      'media-1.api-sports.io',
    ],
  },
};

module.exports = nextConfig;
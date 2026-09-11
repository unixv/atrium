const images = new Map<string, HTMLImageElement>();

export function spriteImage(src: string) {
  let image = images.get(src);
  if (image) return image;

  image = new Image();
  image.src = src;
  images.set(src, image);
  return image;
}

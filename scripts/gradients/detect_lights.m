function [ ] = detect_lights()

for i=1:19
    
    if i < 10
        im1 = double(rgb2gray(imread(['../data/img300x400/SET054/Img001_0' int2str(i) '.bmp'])));
    else
        im1 = double(rgb2gray(imread(['../data/img300x400/SET054/Img001_' int2str(i) '.bmp'])));
    end

    highs = (im1>150) .* im1;
    highs = highs * (1.0/max(highs(:)));
    
        
    [accum,ccen,crad] = CircularHough_Grd(highs*255, [30 60]);
    size(ccen,1)
    
    imagesc(highs), colormap gray, hold on
    for i=1:size(ccen,1)
        DrawCircle(ccen(i,1),ccen(i,2),crad(i),16,'red');
    end
    k = waitforbuttonpress;
end
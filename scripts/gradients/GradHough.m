function [ phi_all,theta_all,rho_all,accum ] = GradHough( data )
%UNTITLED Summary of this function goes here
%   Detailed explanation goes here

%data = double(rgb2gray(imread('radial_gradient5.png')));

means = [];
stddevs = [];
ps = size(data);

accum = zeros(600,122,175);

for row=2:ps(1)-1
    for col=2:ps(2)-1
        samp = data(row,col); % sample a pixel
        phi = abs(data(row,col-1)-data(row,col)) / (abs(data(row-1,col)-data(row,col))+1);
        theta = abs(data(row,col-1)-data(row,col))/2 + abs(data(row-1,col)-data(row,col))/2;
        rho = abs(col*cos(theta)*cos(phi) + row*cos(theta)*sin(phi) + samp*sin(theta));
        %accum(rho,phi,theta)
        if phi>10000
            disp(row)
            disp(col)
        end
        phi_all(row,col) = phi;
        theta_all(row,col) = theta;
        rho_all(row,col) = rho;
        
        accum(floor(rho)+1,floor(phi)+1,floor(theta)+1) = accum(floor(rho)+1,floor(phi)+1,floor(theta)+1)+1;
    end
end

max = 0;
max_rpt = [];

for r=1:600
    for p=1:122
        for t=1:175
            if accum(r,p,t) > max
                max = accum(r,p,t);
                max_rpt = [r p t];
            end
        end
    end
end

disp(max)
disp(max_rpt)

end


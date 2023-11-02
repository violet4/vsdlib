# Stage 1: Build Stage
FROM gentoo/stage3:latest as builder

# Update the system and install necessary tools
RUN emerge --sync && \
    emerge dev-util/cmake sys-devel/gcc sys-devel/make

# Copy your local overlay and ebuild
COPY ./my-local-overlay /usr/local/portage/my-local-overlay
RUN echo 'PORTDIR_OVERLAY="/usr/local/portage/my-local-overlay"' >> /etc/portage/make.conf

# Emerge your package
RUN emerge my-package

# Stage 2: Run Stage
FROM gentoo/stage3:latest

# Copy the built software from the builder stage
COPY --from=builder /usr/bin/my-package /usr/bin/my-package

# Copy any other necessary files from the builder stage
# ...

# Switch to the user created by your ebuild
USER vsdlib

# Specify the command to run your application
CMD ["my-package"]
